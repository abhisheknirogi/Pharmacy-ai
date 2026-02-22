from sqlalchemy import Column, Integer, String, DateTime, Index, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Pharmacy(Base):
    """Pharmacy master data table."""
    
    __tablename__ = "pharmacies"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Core Fields
    name = Column(String(255), nullable=False, index=True)
    address = Column(String(500), nullable=False)
    
    # Contact Info
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    
    # License & Compliance
    license_number = Column(String(100), nullable=True, unique=True)
    
    # Temporal Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_license_number", "license_number"),
        Index("idx_pharmacy_email", "email"),
    )

    def __repr__(self) -> str:
        return f"<Pharmacy(id={self.id}, name='{self.name}')>"
