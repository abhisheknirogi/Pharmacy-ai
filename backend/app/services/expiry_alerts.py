"""Expiry alert service for monitoring expired medicines."""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..models.medicine import Medicine
import logging

logger = logging.getLogger(__name__)


def get_expiring_medicines(db: Session, days_warning: int = 30):
    """Get medicines expiring within the specified number of days."""
    future_date = datetime.utcnow() + timedelta(days=days_warning)
    return db.query(Medicine).filter(
        (Medicine.expiry_date <= future_date) &
        (Medicine.expiry_date > datetime.utcnow())
    ).order_by(Medicine.expiry_date).all()


def get_expired_medicines(db: Session):
    """Get medicines that have already expired."""
    return db.query(Medicine).filter(
        Medicine.expiry_date <= datetime.utcnow()
    ).all()


def mark_medicines_for_removal(db: Session):
    """Mark expired medicines for removal from inventory."""
    expired = get_expired_medicines(db)
    logger.info(f"Found {len(expired)} expired medicines")
    return expired


def generate_expiry_report(db: Session, days_warning: int = 30):
    """Generate comprehensive expiry report."""
    expiring = get_expiring_medicines(db, days_warning)
    expired = get_expired_medicines(db)

    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "expiring_soon": [
            {
                "id": m.id,
                "name": m.name,
                "batch": m.batch_no,
                "expiry_date": m.expiry_date.isoformat() if m.expiry_date else None,
                "days_left": (m.expiry_date - datetime.utcnow()).days if m.expiry_date else None,
                "stock": m.stock_qty
            }
            for m in expiring
        ],
        "expired": [
            {
                "id": m.id,
                "name": m.name,
                "batch": m.batch_no,
                "expiry_date": m.expiry_date.isoformat() if m.expiry_date else None,
                "stock": m.stock_qty
            }
            for m in expired
        ],
        "summary": {
            "expiring_count": len(expiring),
            "expired_count": len(expired),
            "total_at_risk": len(expiring) + len(expired)
        }
    }
    return report
