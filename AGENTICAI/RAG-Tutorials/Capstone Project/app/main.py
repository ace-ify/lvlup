from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from typing import Dict, Any

from app.config import get_settings
from app.models import ChatRequest, ChatResponse, HealthResponse, MetricResponse, ErrorResponse
from app.security import SecurityPipeline
from app.cache import ResponseCache
from app.monitoring import get_logger, MetricsCollector, RequestTimer
from app.agent import compiled_agent

logger = get_logger("production-api")
settings = get_settings()

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    logger.info(f"Starting application in environment: {settings.app_env}")
    
    # Initialize cache, security pipeline, and metrics collector
    app.state.cache = ResponseCache(
        redis_url=settings.redis_url,
        use_redis=settings.use_redis,
        ttl_seconds=settings.cache_ttl_seconds
    )
    app.state.security = SecurityPipeline()
    app.state.metrics = MetricsCollector()
    
    yield
    
    # Shutdown: Clean up resources
    logger.info("Shutting down application...")
    if hasattr(app.state, "cache") and app.state.cache.redis_client:
        try:
            app.state.cache.redis_client.close()
        except Exception as e:
            logger.warning(f"Error closing Redis connection during shutdown: {e}")

app = FastAPI(title="Production RAG API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=ErrorResponse(
            error="RateLimitExceeded",
            detail=f"Rate limit exceeded: {exc.detail}"
        ).model_dump()
    )

@app.post("/chat", response_model=ChatResponse, responses={
    400: {"model": ErrorResponse},
    429: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
@limiter.limit(settings.rate_limit)
async def chat_endpoint(request: ChatRequest, fastapi_req: Request):
    """
    Production-ready Chat/RAG endpoint.
    Orchestrates Rate Limiting, Security Sanitization, Semantic Caching,
    LangGraph Agentic Brain with Fallback, Output Validation, and Telemetry.
    """
    metrics: MetricsCollector = fastapi_req.app.state.metrics
    cache: ResponseCache = fastapi_req.app.state.cache
    security: SecurityPipeline = fastapi_req.app.state.security

    with RequestTimer() as timer:
        # Step 1: Security check input
        is_allowed, cleaned_text, input_notes = security.check_input(request.message)
        if not is_allowed:
            # Blocked prompt injection
            metrics.record_request(latency_ms=timer.latency_ms, error=True)
            logger.warning(f"Request blocked by security check: {input_notes}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Security check failed: {input_notes[0] if input_notes else 'Unsafe input'}"
            )

        # Step 2: Caching check
        cached_response = cache.get(cleaned_text)
        if cached_response is not None:
            # Cache hit!
            logger.info("Cache hit! Returning response immediately.")
            metrics.record_request(
                latency_ms=timer.latency_ms,
                input_tokens=0,
                output_tokens=0,
                error=False,
                cache_hit=True
            )
            return ChatResponse(
                response=cached_response,
                thread_id=request.thread_id or "default",
                model_used="cache",
                cached=True,
                processing_time_ms=timer.latency_ms
            )

        # Step 3: Invoke the LangGraph agent
        try:
            logger.info("Cache miss. Invoking agent.")
            result = compiled_agent.invoke({
                "message": cleaned_text,
                "errors": []
            })
            
            agent_response = result.get("response", "")
            model_used = result.get("model_used", "unknown")
            
            # Record if it is an error from models failing
            has_error = (model_used == "none")
            
        except Exception as e:
            logger.exception("Agent invocation failed completely.")
            metrics.record_request(latency_ms=timer.latency_ms, error=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal server error occurred while processing your request."
            )

        # Step 4: Security check output (only if we didn't return technical difficulties apology)
        cleaned_output = agent_response
        output_warnings = []
        if model_used != "none":
            cleaned_output, output_warnings = security.check_output(agent_response)
            if output_warnings:
                logger.warning(f"Security warnings in output: {output_warnings}")

        # Step 5: Save response to cache if it was successfully generated
        # If we had a model failure (model_used == "none"), we do not cache the error message!
        if model_used != "none":
            cache.set(cleaned_text, cleaned_output)

        # Step 6: Record Metrics
        input_tokens = len(cleaned_text) // 4
        output_tokens = len(cleaned_output) // 4
        metrics.record_request(
            latency_ms=timer.latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            error=has_error,
            cache_hit=False
        )

        return ChatResponse(
            response=cleaned_output,
            thread_id=request.thread_id or "default",
            model_used=model_used,
            cached=False,
            processing_time_ms=timer.latency_ms
        )

@app.get("/health", response_model=HealthResponse)
async def health_endpoint(fastapi_req: Request):
    cache: ResponseCache = fastapi_req.app.state.cache
    
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

@app.get("/metrics", response_model=MetricResponse)
async def metrics_endpoint(fastapi_req: Request):
    metrics: MetricsCollector = fastapi_req.app.state.metrics
    return MetricResponse(**metrics.get_metrics())
