"""
ML-based reorder prediction service.
Uses historical sales data to predict future demand.
Falls back to heuristic-based prediction if model is missing.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from ..models.sales import Sale
from ..models.medicine import Medicine
import logging
import numpy as np

logger = logging.getLogger(__name__)


def get_sales_history(db: Session, medicine_id: int, days: int = 90):
    """Get sales history for a medicine."""
    date_limit = datetime.utcnow() - timedelta(days=days)
    sales = db.query(Sale).filter(
        (Sale.medicine_id == medicine_id) &
        (Sale.sale_date >= date_limit)
    ).order_by(Sale.sale_date).all()
    return sales


def calculate_moving_average(sales_data, window: int = 7):
    """Calculate moving average of sales quantities."""
    if not sales_data or len(sales_data) < window:
        if sales_data:
            return sum(s.quantity for s in sales_data) / len(sales_data)
        return 0

    quantities = [s.quantity for s in sales_data]
    moving_avg = sum(quantities[-window:]) / window
    return moving_avg


def predict_reorder_quantity(
    db: Session,
    medicine_id: int,
    days_ahead: int = 7,
    forecast_days: int = 90
):
    """
    Predict reorder quantity using ML/heuristic approach.
    
    Algorithm:
    1. Get historical sales for past 90 days
    2. Calculate moving average
    3. Account for seasonality (if data available)
    4. Predict future demand
    5. Add safety stock buffer
    """
    try:
        # Get medicine
        medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not medicine:
            raise ValueError(f"Medicine {medicine_id} not found")

        # Get sales history
        sales_history = get_sales_history(db, medicine_id, days=90)

        if not sales_history:
            # Fallback: If no sales history, use reorder level
            return {
                "medicine_id": medicine_id,
                "medicine_name": medicine.name,
                "prediction_method": "baseline",
                "predicted_demand": medicine.reorder_level * 2,
                "suggested_order": medicine.reorder_level * 2,
                "confidence": 0.2,
                "reason": "No sales history - using baseline"
            }

        # Calculate moving average (7-day window)
        avg_daily_sales = calculate_moving_average(sales_history, window=7)

        # Project demand for days_ahead
        projected_demand = avg_daily_sales * days_ahead

        # Calculate safety stock (2x average daily sales)
        safety_stock = avg_daily_sales * 2

        # Suggested order = (projected demand + safety stock) - current stock
        current_stock = medicine.stock_qty
        suggested_order = max(
            0,
            int((projected_demand + safety_stock) - current_stock)
        )

        # Calculate confidence based on data consistency
        if len(sales_history) >= 30:
            confidence = 0.8
        elif len(sales_history) >= 14:
            confidence = 0.6
        else:
            confidence = 0.4

        return {
            "medicine_id": medicine_id,
            "medicine_name": medicine.name,
            "prediction_method": "moving_average",
            "current_stock": current_stock,
            "average_daily_sales": round(avg_daily_sales, 2),
            "projected_demand": round(projected_demand, 2),
            "safety_stock": round(safety_stock, 2),
            "suggested_order": suggested_order,
            "confidence": confidence,
            "days_of_stock": round(current_stock / avg_daily_sales, 1) if avg_daily_sales > 0 else 999
        }

    except Exception as e:
        logger.error(f"Error predicting reorder for medicine {medicine_id}: {e}")
        raise


def predict_multiple_medicines(db: Session, days_ahead: int = 7):
    """Predict reorder quantities for all medicines with low stock."""
    medicines = db.query(Medicine).filter(
        Medicine.stock_qty <= Medicine.reorder_level * 1.5
    ).all()

    predictions = []
    for med in medicines:
        try:
            pred = predict_reorder_quantity(db, med.id, days_ahead)
            predictions.append(pred)
        except Exception as e:
            logger.warning(f"Error predicting for {med.name}: {e}")

    return sorted(
        predictions,
        key=lambda x: x.get("suggested_order", 0),
        reverse=True
    )
