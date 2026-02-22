from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class MedicineCreate(BaseModel):
    """Schema for creating a new medicine with comprehensive validation."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Medicine name",
        example="Aspirin"
    )
    generic_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Generic/chemical name of the medicine"
    )
    batch_no: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Batch number",
        example="BATCH-2024-001"
    )
    expiry_date: Optional[datetime] = Field(
        None,
        description="Medicine expiry date"
    )
    stock_qty: int = Field(
        ...,
        ge=0,
        description="Stock quantity in units",
        example=100
    )
    reorder_level: int = Field(
        10,
        ge=1,
        description="Reorder level threshold",
        example=10
    )
    price: float = Field(
        ...,
        gt=0,
        description="Price per unit",
        example=9.99
    )
    manufacturer: Optional[str] = Field(
        None,
        max_length=255,
        description="Manufacturer name"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Detailed description of the medicine"
    )

    @field_validator("stock_qty")
    @classmethod
    def validate_stock_qty(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Stock quantity cannot be negative")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Price must be greater than zero")
        if v > 999999.99:
            raise ValueError("Price exceeds maximum allowed value")
        return round(v, 2)

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v < datetime.utcnow():
            raise ValueError("Expiry date cannot be in the past")
        return v


class MedicineUpdate(BaseModel):
    """Schema for updating a medicine with optional fields."""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255
    )
    stock_qty: Optional[int] = Field(
        None,
        ge=0
    )
    price: Optional[float] = Field(
        None,
        gt=0
    )
    expiry_date: Optional[datetime] = None
    reorder_level: Optional[int] = Field(
        None,
        ge=1
    )

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v <= 0:
                raise ValueError("Price must be greater than zero")
            if v > 999999.99:
                raise ValueError("Price exceeds maximum allowed value")
            return round(v, 2)
        return v


class MedicineResponse(MedicineCreate):
    """Response schema for medicine with database-generated fields."""
    
    id: int = Field(..., description="Unique medicine identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
