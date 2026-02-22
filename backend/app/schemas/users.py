"""
User-related Pydantic schemas for authentication and profile management.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 chars, must include uppercase, lowercase, digit)"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="User's full name"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Response schema for user data."""
    
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="User's full name")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """Schema for JWT token claims."""
    
    email: Optional[str] = Field(None, description="User email from token")
    exp: Optional[int] = Field(None, description="Token expiration timestamp")
