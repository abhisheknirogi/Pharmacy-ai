"""
Middleware for PharmaRec API.
Includes error handling, request logging, security headers, and monitoring.
"""

import logging
import time
from typing import Callable
from uuid import uuid4

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .exceptions import PharmaRecException


logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to handle exceptions and return proper error responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            # Add request tracking ID
            request.state.request_id = str(uuid4())
            response = await call_next(request)
            return response
        except PharmaRecException as exc:
            logger.warning(
                f"PharmaRec exception: {exc.error_code}",
                extra={
                    "request_id": request.state.request_id if hasattr(request.state, 'request_id') else None,
                    "path": request.url.path,
                    "method": request.method,
                    "error_code": exc.error_code,
                    "message": exc.message,
                }
            )
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.dict(),
            )
        except Exception as exc:
            # Log unexpected exceptions
            logger.error(
                f"Unexpected exception: {str(exc)}",
                exc_info=True,
                extra={
                    "request_id": request.state.request_id if hasattr(request.state, 'request_id') else None,
                    "path": request.url.path,
                    "method": request.method,
                }
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "request_id": request.state.request_id if hasattr(request.state, 'request_id') else None,
                },
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.state.request_id if hasattr(request.state, 'request_id') else str(uuid4())
        
        # Skip logging for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        start_time = time.time()
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None,
            }
        )
        
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for basic rate limiting (can be replaced with Redis-based for production)."""
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: dict = {}  # {client_ip: [(timestamp, count), ...]}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for certain paths
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        # Initialize client record
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old requests outside the window
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if ts > window_start
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit of {self.requests_per_minute} requests per minute exceeded",
                }
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        # Clean up old clients
        if len(self.requests) > 1000:
            self.requests = {k: v for k, v in self.requests.items() if v}
        
        return await call_next(request)
