import time
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from langsmith import traceable
from dotenv import load_dotenv

from app.config import get_settings
from app.models import (
    ChatRequest, ChatResponse,
    HealthResponse, MetricsResponse, ErrorResponse,
)
from app.security import SecurityPipeline
from app.cache import ResponseCache
from app.monitoring import get_logger, MetricsCollector, RequestTimer
from app.agent import ProductionAgent

load_dotenv()

logger = get_logger("production-api")
settings = get_settings()

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    logger.info("Starting production API...", extra={"extra_data": {
        "environment": settings.app_env,
        "primary_model": settings.primary_model,
        "tracing_enabled": settings.langchain_tracing_v2,
    }})
    
    # Initialize components
    security = SecurityPipeline()
    cache = ResponseCache(ttl_seconds=settings.cache_ttl_seconds)
    metrics = MetricsCollector()
    agent = ProductionAgent()

    logger.info("All components initialized. Ready to serve requests.")
    
    # Expose them to app state so endpoints can access them
    app.state.security = security
    app.state.cache = cache
    app.state.metrics = metrics
    app.state.agent = agent
    
    yield # App is running
    
    # Shutdown: Clean up resources
    logger.info("Shutting down...", extra={"extra_data": metrics.summary})
    if cache.redis_client:
        try:
            cache.redis_client.close()
        except Exception as e:
            logger.warning(f"Error closing Redis connection during shutdown: {e}")

app = FastAPI(title="Production RAG API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "RateLimitExceeded",
            "detail": "Too many requests. Please slow down.",
        }
    )

@app.post("/chat", response_model=ChatResponse)
@limiter.limit(settings.rate_limit)
@traceable(name="chat_endpoint")
async def chat(request: Request, body: ChatRequest):
    """
    Main chat endpoint.
    Flow: Rate Limiting -> Security Sanitization -> Semantic Caching ->
          LangGraph Agent (with Fallback) -> Output Validation -> Telemetry Logging.
    """
    metrics: MetricsCollector = request.app.state.metrics
    cache: ResponseCache = request.app.state.cache
    security: SecurityPipeline = request.app.state.security
    agent: ProductionAgent = request.app.state.agent

    with RequestTimer() as timer:
        # Step 1: Security check input
        is_allowed, cleaned_text, input_notes = security.check_input(body.message)
        if not is_allowed:
            # Blocked prompt injection
            metrics.record_request(latency_ms=timer.elapsed_ms, error=True)
            logger.warning(f"Request blocked by security check: {input_notes}")
            raise HTTPException(
                status_code=400,
                detail=f"Security check failed: {input_notes[0] if input_notes else 'Unsafe input'}"
            )

        # Step 2: Caching check
        cached_response = cache.get(cleaned_text)
        if cached_response is not None:
            # Cache hit!
            logger.info("Cache hit! Returning response immediately.")
            metrics.record_request(
                latency_ms=timer.elapsed_ms,
                input_tokens=0,
                output_tokens=0,
                error=False,
                cache_hit=True
            )
            return ChatResponse(
                response=cached_response,
                thread_id=body.thread_id or "default",
                model_used="cache",
                cached=True,
                processing_time_ms=round(timer.elapsed_ms, 2)
            )

        # Step 3: Invoke the LangGraph agent
        try:
            logger.info("Cache miss. Invoking agent.")
            result = agent.invoke(cleaned_text)
            
            agent_response = result.get("response", "")
            model_used = result.get("model_used", "unknown")
            
            # Record if it is an error from models failing
            has_error = (model_used == "error_handler" or result.get("error") is not None)
            
        except Exception as e:
            logger.exception("Agent invocation failed completely.")
            metrics.record_request(latency_ms=timer.elapsed_ms, error=True)
            raise HTTPException(
                status_code=500,
                detail="An internal server error occurred while processing your request."
            )

        # Step 4: Security check output (only if we didn't return technical difficulties apology)
        validated_response = agent_response
        output_warnings = []
        if model_used != "error_handler":
            validated_response, output_warnings = security.check_output(agent_response)
            if output_warnings:
                logger.warning(f"Security warnings in output: {output_warnings}")

        # Step 5: Save response to cache if it was successfully generated
        # If we had a model failure (model_used == "error_handler"), we do not cache the error message!
        if model_used != "error_handler":
            cache.set(cleaned_text, validated_response)

        # Step 6: Record Metrics
        input_tokens = len(cleaned_text) // 4
        output_tokens = len(validated_response) // 4
        metrics.record_request(
            latency_ms=timer.elapsed_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            error=has_error,
            cache_hit=False
        )

        logger.info("Request completed", extra={"extra_data": {
            "thread_id": body.thread_id,
            "model_used": model_used,
            "latency_ms": round(timer.elapsed_ms, 2),
        }})

        return ChatResponse(
            response=validated_response,
            thread_id=body.thread_id or "default",
            model_used=model_used,
            cached=False,
            processing_time_ms=round(timer.elapsed_ms, 2),
        )

@app.get("/health", response_model=HealthResponse)
async def health_endpoint(request: Request):
    cache: ResponseCache = request.app.state.cache
    
    # Check components
    cache_ok = True
    if cache.use_redis and cache.redis_client:
        try:
            cache.redis_client.ping()
        except Exception:
            cache_ok = False
            
    checks = {
        "security": True,
        "cache": cache_ok,
        "agent": True
    }
    
    status_str = "healthy" if cache_ok else "degraded"
    
    return HealthResponse(
        status=status_str,
        environment=settings.app_env,
        version="1.0.0",
        checks=checks
    )

@app.get("/metrics", response_model=MetricsResponse)
async def metrics_endpoint(request: Request):
    metrics: MetricsCollector = request.app.state.metrics
    return MetricsResponse(**metrics.get_metrics())
