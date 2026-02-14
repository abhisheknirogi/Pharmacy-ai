"""
Standardized API responses for PharmaRec.
Ensures consistent response format across all endpoints.
"""

from typing import Any, Dict, List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field


T = TypeVar("T")


class Meta(BaseModel):
    """Metadata for paginated responses."""
    current_page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether next page exists")
    has_prev: bool = Field(..., description="Whether previous page exists")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    success: bool = True
    data: List[T] = Field(..., description="Response data")
    meta: Meta = Field(..., description="Pagination metadata")
    message: Optional[str] = None


class SuccessResponse(BaseModel, Generic[T]):
    """Generic success response wrapper."""
    success: bool = True
    data: T = Field(..., description="Response data")
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    request_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    status_code: int


class CreatedResponse(BaseModel, Generic[T]):
    """Response for resource creation."""
    success: bool = True
    data: T = Field(..., description="Created resource")
    message: str = "Resource created successfully"


class UpdatedResponse(BaseModel, Generic[T]):
    """Response for resource update."""
    success: bool = True
    data: T = Field(..., description="Updated resource")
    message: str = "Resource updated successfully"


class DeletedResponse(BaseModel):
    """Response for resource deletion."""
    success: bool = True
    message: str = "Resource deleted successfully"
    deleted_id: Any


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Health status")
    app: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    timestamp: Optional[str] = None


def create_paginated_response(
    data: List[T],
    current_page: int,
    page_size: int,
    total_items: int,
    message: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standardized paginated response."""
    total_pages = (total_items + page_size - 1) // page_size
    has_next = current_page < total_pages
    has_prev = current_page > 1
    
    return {
        "success": True,
        "data": data,
        "meta": {
            "current_page": current_page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
        },
        "message": message,
    }
