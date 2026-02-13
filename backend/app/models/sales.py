# backend/app/models/sales.py

from sqlalchemy import Column, Integer, String, Float, Date
from app.database import Base

class Sales(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    medicine_name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    date = Column(Date)
 