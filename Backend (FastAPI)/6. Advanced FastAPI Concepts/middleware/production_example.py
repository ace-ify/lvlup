import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from pydantic_settings import BaseSettings

# =========================================================================
# MIDDLEWARE LIFECYCLE & EXECUTION ORDER DIAGRAM
# (Onion Architecture: Last registered runs first on request, last on response)
#
#                  Incoming Request 
#                         │
#                         ▼
# ┌──────────────────────────────────────────────────┐
# │ 1. add_process_time_header (Outermost Layer)     │ ◄── Timer starts
# │   ┌──────────────────────────────────────────────┤
# │   │ 2. log_and_protect                           │ ◄── Logs incoming path
# │   │   ┌──────────────────────────────────────────┤
# │   │   │ 3. GZipMiddleware                        │ ◄── Checks zip compression
# │   │   │   ┌──────────────────────────────────────┤
# │   │   │   │ 4. CORSMiddleware (Innermost Layer)  │ ◄── Checks domain security
# │   │   │   │   ┌──────────────────────────────────┤
# │   │   │   │   │    ACTUAL ROUTE: hello()         │ ◄── Endpoint executes
# │   │   │   │   └──────────────────────────────────┤
# │   │   │   │ 4. CORSMiddleware (Response)         │ ─── Adds CORS headers
# │   │   │   └──────────────────────────────────────┤
# │   │   │ 3. GZipMiddleware (Response)             │ ─── Compresses body if large
# │   │   └──────────────────────────────────────────┤
# │   │ 2. log_and_protect (Response)                │ ─── Catches crashes/errors
# │   └──────────────────────────────────────────────┤
# │ 1. add_process_time_header (Response)            │ ─── Calculates & injects X-Process-Time
# └──────────────────────────────────────────────────┘
#                         │
#                         ▼
#                  Client Response
# =========================================================================


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("production_app")

# 1. Environment Configurations (Production Best Practice)
class Settings(BaseSettings):
    # In production, this list would be loaded from your .env file
    # e.g. CORS_ORIGINS=["https://my-app.com", "https://admin.my-app.com"]
    cors_origins: list[str] = ["http://localhost:3000", "https://my-frontend.com"]
    gzip_min_size: int = 1000  # Compress responses larger than 1KB
    environment: str = "production"

settings = Settings()
app = FastAPI(title="Production Middleware Demo")

# ==========================================
# 2. BUILT-IN MIDDLEWARES (Registered First)
# ==========================================

# A. CORS Middleware: Must be configured with explicit origins in production (no '*')
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["X-Process-Time"]  # Expose custom headers so frontend JS can read it
)

# B. GZip Middleware: Compress large responses automatically
app.add_middleware(
    GZipMiddleware, 
    minimum_size=settings.gzip_min_size
)

# ==========================================
# 3. CUSTOM DECORATOR MIDDLEWARES (Registered Last, Runs First)
# ==========================================

# A. Request Logging and Error Catching Middleware
@app.middleware("http")
async def log_and_protect(request: Request, call_next):
    logger.info(f"Incoming Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        # Catch unexpected crashes, log them, and prevent server crash
        logger.error(f"Request failed: {exc}", exc_info=True)
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected internal server error occurred."}
        )

# B. Process Timer & Custom Headers Injector Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Inject timing info into response headers so frontend can read it
    response.headers["X-Process-Time"] = f"{process_time:.5f}s"
    return response

# ==========================================
# 4. ENDPOINTS
# ==========================================

@app.get("/hello")
async def hello():
    # Simulate database or heavy work
    time.sleep(0.05)
    return {"message": "Hello from production-grade middleware setup!"}
