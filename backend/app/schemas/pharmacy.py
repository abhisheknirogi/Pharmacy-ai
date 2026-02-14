from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class PharmacyCreate(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    license_number: Optional[str] = None


class PharmacyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    license_number: Optional[str] = None


class PharmacyResponse(PharmacyCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
