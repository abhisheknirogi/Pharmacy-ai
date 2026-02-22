from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Medicine(Base):
    """Medicine master table for pharmacy inventory management."""
    
    __tablename__ = "medicines"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Core Fields
    name = Column(String(255), nullable=False, index=True)
    generic_name = Column(String(255), nullable=True)
    batch_no = Column(String(100), nullable=False)
    
    # Inventory Fields
    stock_qty = Column(Integer, default=0, nullable=False)
    reorder_level = Column(Integer, default=10, nullable=False)
    
    # Pricing
    price = Column(Float, nullable=False)
    
    # Metadata
    manufacturer = Column(String(255), nullable=True)
    description = Column(String(1000), nullable=True)
    
    # Temporal Fields
    expiry_date = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("stock_qty >= 0", name="check_stock_qty_non_negative"),
        CheckConstraint("reorder_level >= 1", name="check_reorder_level_positive"),
        CheckConstraint("price > 0", name="check_price_positive"),
        Index("idx_name_generic", "name", "generic_name"),
        Index("idx_expiry_date", "expiry_date"),
        Index("idx_batch_no", "batch_no"),
    )

    def __repr__(self) -> str:
        return f"<Medicine(id={self.id}, name='{self.name}', stock_qty={self.stock_qty})>"

    @property
    def is_low_stock(self) -> bool:
        """Check if medicine stock is low."""
        return self.stock_qty <= self.reorder_level

    @property
    def is_expired(self) -> bool:
        """Check if medicine has expired."""
        if not self.expiry_date:
            return False
        return self.expiry_date < datetime.utcnow()
