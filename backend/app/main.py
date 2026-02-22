"""
PharmaRec AI - FastAPI Main Application

Pharmacy inventory, sales, and AI-powered reorder prediction system.
Production-ready with comprehensive error handling, middleware, and monitoring.
"""

import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from .database import init_db, close_db
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
    """
    Application lifecycle management - startup and shutdown events.
    
    Startup:
    - Initialize database and create tables
    - Log application startup
    
    Shutdown:
    - Close database connections
    - Cleanup resources
    """
    # ==================== STARTUP ====================
    try:
        logger.info(f"Initializing {settings.APP_NAME} v{settings.APP_VERSION}...")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Debug mode: {settings.DEBUG}")
        
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
        
        logger.info(f"{settings.APP_NAME} started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # ==================== SHUTDOWN ====================
    try:
        logger.info("Shutting down application...")
        close_db()
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)


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

# ==================== MIDDLEWARE STACK ====================
# Order matters - executed in reverse order (LIFO)

# Exception handling (outermost - catches all unhandled exceptions)
app.add_middleware(ErrorHandlingMiddleware)

# Security headers (apply to all responses)
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting (before request logging to track attempt counts)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE
)

# Request/response logging (after security, before CORS)
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware (last in chain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ==================== HEALTH & DIAGNOSTICS ====================

@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Health check endpoint",
    description="Returns application health status for monitoring and load balancer health checks",
)
def health_check() -> HealthCheckResponse:
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
    - status: Current application status (healthy/degraded/unhealthy)
    - app: Application name
    - version: Application version
    - timestamp: Current server time (UTC)
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(
    "/version",
    tags=["Info"],
    summary="Get application version",
    description="Returns application version and environment information",
    responses={200: {"description": "Version information"}}
)
def get_version() -> Dict[str, Any]:
    """Get application version and build information."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database_type": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(
    "/diagnostics",
    tags=["Info"],
    summary="Get application diagnostics",
    description="Returns application diagnostics including memory, CPU, and configuration status"
)
def get_diagnostics() -> Dict[str, Any]:
    """Get application diagnostics (admin endpoint)."""
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "memory_usage_mb": round(process.memory_info().rss / 1024 / 1024, 2),
            "cpu_percent": process.cpu_percent(interval=1),
            "timestamp": datetime.utcnow().isoformat(),
            "database_configured": bool(settings.DATABASE_URL),
            "ml_enabled": settings.USE_ML_FALLBACK,
            "pdf_parsing_enabled": settings.ENABLE_PDF_PARSING,
        }
    except Exception as e:
        logger.error(f"Diagnostics check failed: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e),
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }


# ==================== API ROUTERS ====================

app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(inventory.router, prefix="/api/v1", tags=["Inventory"])
app.include_router(sales.router, prefix="/api/v1", tags=["Sales"])
app.include_router(reorder.router, prefix="/api/v1", tags=["Reorder"])
app.include_router(pdf_parser.router, prefix="/api/v1", tags=["PDF Parser"])

# Optional routers
try:
    from .api.routes import preview
    app.include_router(preview.router, tags=["Preview"])
except Exception as e:
    logger.debug(f"Preview router not available: {str(e)}")


# ==================== STARTUP LOGGING ====================

if __name__ == "__main__":
    logger.info(f"Application: {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("OpenAPI documentation available at: /docs")
    if settings.DEBUG:
        logger.warning("⚠️  DEBUG MODE ENABLED - Do not use in production!")

