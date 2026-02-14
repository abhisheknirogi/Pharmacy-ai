from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=True)
    medicine_name = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    sale_date = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    medicine = relationship("Medicine", backref="sales")
