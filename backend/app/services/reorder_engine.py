from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.sales import Sale
from ..models.medicine import Medicine
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def generate_reorder_list(db: Session, days_to_analyze: int = 7):
    """
    Calculates what medicines need to be ordered based on sales velocity.
    Uses simple heuristic: if current stock < 3 days of average sales, suggest reorder.
    """
    reorder_suggestions = []

    try:
        # 1. Get average sales per medicine in the last X days
        date_limit = datetime.utcnow() - timedelta(days=days_to_analyze)

        # Query sales velocity
        sales_velocity = db.query(
            Sale.medicine_name,
            func.sum(Sale.quantity).label('total_sold')
        ).filter(Sale.sale_date >= date_limit).group_by(
            Sale.medicine_name
        ).all()

        for item in sales_velocity:
            try:
                # 2. Compare with current stock in Inventory
                med = db.query(Medicine).filter(
                    Medicine.name.ilike(item.medicine_name)
                ).first()

                if med:
                    daily_avg = item.total_sold / days_to_analyze if days_to_analyze > 0 else 0
                    # Threshold: If stock is less than 3 days of average sales
                    threshold = daily_avg * 3
                    if med.stock_qty < threshold:
                        reorder_suggestions.append({
                            "medicine_id": med.id,
                            "medicine_name": med.name,
                            "current_stock": med.stock_qty,
                            "daily_average": round(daily_avg, 2),
                            "suggested_order_qty": int(daily_avg * 10),  # Order for 10 days
                            "priority": "CRITICAL" if med.stock_qty == 0 else (
                                "HIGH" if med.stock_qty < daily_avg else "MEDIUM"
                            ),
                            "reorder_level": med.reorder_level
                        })
            except Exception as e:
                logger.warning(f"Error processing medicine {item.medicine_name}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error generating reorder list: {e}")

    return sorted(reorder_suggestions, key=lambda x: (
        {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}.get(x.get("priority", "LOW"), 3)
    ))


def get_low_stock_medicines(db: Session):
    """Get medicines that are below reorder level."""
    return db.query(Medicine).filter(
        Medicine.stock_qty <= Medicine.reorder_level
    ).all()


def check_expiry_medicines(db: Session, days_warning: int = 30):
    """Get medicines expiring within specified days."""
    future_date = datetime.utcnow() + timedelta(days=days_warning)
    return db.query(Medicine).filter(
        (Medicine.expiry_date <= future_date) &
        (Medicine.expiry_date > datetime.utcnow())
    ).all()
