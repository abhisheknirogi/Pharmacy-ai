from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SaleCreate(BaseModel):
    medicine_id: Optional[int] = None
    medicine_name: str
    quantity: int
    unit_price: float
    total_amount: Optional[float] = None


class SaleResponse(SaleCreate):
    id: int
    sale_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class SaleSummary(BaseModel):
    medicine_name: str
    total_quantity: int
    total_amount: float
    transaction_count: int
