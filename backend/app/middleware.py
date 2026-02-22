"""
Middleware for PharmaRec API.
Includes error handling, request logging, security headers, request validation, and monitoring.
"""

import logging
import time
import json
from typing import Callable, Dict, Any
from uuid import uuid4

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
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
        except RequestValidationError as exc:
            request_id = request.state.request_id if hasattr(request.state, 'request_id') else str(uuid4())
            logger.warning(
                f"Validation error: {exc.error_count()} validation error(s)",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "error_count": exc.error_count(),
                }
            )
            return JSONResponse(
                status_code=422,
                content={
                    "error": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "request_id": request_id,
                    "details": exc.errors(),
                },
            )
        except PharmaRecException as exc:
            request_id = request.state.request_id if hasattr(request.state, 'request_id') else str(uuid4())
            logger.warning(
                f"PharmaRec exception: {exc.error_code}",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "error_code": exc.error_code,
                    "message": exc.message,
                }
            )
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.dict() | {"request_id": request_id},
            )
        except Exception as exc:
            # Log unexpected exceptions with full traceback
            request_id = request.state.request_id if hasattr(request.state, 'request_id') else str(uuid4())
            logger.error(
                f"Unexpected exception: {type(exc).__name__}: {str(exc)}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "exception_type": type(exc).__name__,
                }
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please contact support if this persists.",
                    "request_id": request_id,
                    "status_code": 500,
                },
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses with structured logging."""
    
    # Paths to skip logging
    SKIP_LOGGING_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.state.request_id if hasattr(request.state, 'request_id') else str(uuid4())
        
        # Skip logging for certain paths
        if request.url.path in self.SKIP_LOGGING_PATHS:
            return await call_next(request)
        
        start_time = time.time()
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": dict(request.query_params) if request.query_params else None,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request failed: {str(e)}", extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
            })
            raise
        
        # Log response
        duration = time.time() - start_time
        log_level = "info" if response.status_code < 400 else "warning"
        getattr(logger, log_level)(
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
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for basic rate limiting (can be replaced with Redis-based for production)."""
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}  # {client_ip: [timestamp, ...]}
    
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
            request_id = request.state.request_id if hasattr(request.state, 'request_id') else str(uuid4())
            logger.warning(
                f"Rate limit exceeded for {client_ip}",
                extra={
                    "request_id": request_id,
                    "client_ip": client_ip,
                    "limit": self.requests_per_minute,
                }
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit of {self.requests_per_minute} requests per minute exceeded",
                    "request_id": request_id if hasattr(request.state, 'request_id') else None,
                    "status_code": 429,
                }
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        # Clean up old clients periodically
        if len(self.requests) > 1000:
            # Remove clients with no recent requests
            current_time_check = time.time()
            self.requests = {
                k: v for k, v in self.requests.items()
                if any(ts > current_time_check - 60 for ts in v)
            }
        
        return await call_next(request)

