from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MedicineCreate(BaseModel):
    name: str
    generic_name: Optional[str] = None
    batch_no: str
    expiry_date: Optional[datetime] = None
    stock_qty: int
    reorder_level: int = 10
    price: float
    manufacturer: Optional[str] = None
    description: Optional[str] = None


class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    stock_qty: Optional[int] = None
    price: Optional[float] = None
    expiry_date: Optional[datetime] = None
    reorder_level: Optional[int] = None


class MedicineResponse(MedicineCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
