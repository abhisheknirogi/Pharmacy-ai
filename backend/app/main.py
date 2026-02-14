"""
PharmaRec AI - FastAPI Main Application
Pharmacy inventory, sales, and AI-powered reorder prediction system.

Production-ready with comprehensive error handling, middleware, and monitoring.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime

from .database import init_db, engine, Base
from .config import settings
from .api.routes import auth, inventory, sales, reorder, pdf_parser
from .utils.logging import setup_logging
from .middleware import (
    ErrorHandlingMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
)
from .responses import HealthCheckResponse

# Setup logging
logger = setup_logging("pharmarec.main", logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App startup and shutdown events."""
    # Startup: Initialize database
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown: Cleanup if needed
    logger.info("Shutting down application")


# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered pharmacy inventory and sales management system",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# Add middleware stack (order matters - executed in reverse)
# Exception handling (should be first to catch all errors)
app.add_middleware(ErrorHandlingMiddleware)

# Security headers (apply to all responses)
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting (before request logging to track attempts)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# Request/response logging (after security, before CORS)
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware (permissive for now, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Always returns 200 OK if the service is running.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }


# Include routers
app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(inventory.router, prefix="/api", tags=["Inventory"])
app.include_router(sales.router, prefix="/api", tags=["Sales"])
app.include_router(reorder.router, prefix="/api", tags=["Reorder"])
app.include_router(pdf_parser.router, prefix="/api", tags=["PDF Parser"])

# Version and info endpoints
@app.get("/version")
def get_version():
    """Get application version and build information."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": "production" if not settings.DEBUG else "development",
        "debug": settings.DEBUG,
        "database_type": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/diagnostics")
def get_diagnostics():
    """Get application diagnostics (admin endpoint)."""
    import psutil
    import os
    
    try:
        process = psutil.Process(os.getpid())
        
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "memory_usage_mb": round(process.memory_info().rss / 1024 / 1024, 2),
            "cpu_percent": process.cpu_percent(interval=1),
            "startup_timestamp": datetime.utcnow().isoformat(),
            "database_url_set": bool(settings.DATABASE_URL),
            "secret_key_set": bool(settings.SECRET_KEY),
        }
    except Exception as e:
        logger.error(f"Diagnostics check failed: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e),
        }


logger.info(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} FastAPI app initialized")
logger.info(f"📚 OpenAPI docs available at: /docs")
if settings.DEBUG:
    logger.warning("⚠️  DEBUG MODE ENABLED - Do not use in production!")
