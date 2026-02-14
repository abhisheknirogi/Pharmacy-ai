from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    generic_name = Column(String, nullable=True)
    batch_no = Column(String)
    expiry_date = Column(DateTime, nullable=True)
    stock_qty = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    price = Column(Float)
    manufacturer = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
