from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ...database import get_db
from ...services.reorder_engine import generate_reorder_list
from ...ml_client.reorder_predictor import predict_reorder_quantity

router = APIRouter(prefix="/reorder", tags=["Reorder"])


@router.get("/suggestions")
def get_reorder_suggestions(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get AI-based reorder suggestions."""
    try:
        suggestions = generate_reorder_list(db, days_to_analyze=days)
        return {
            "status": "success",
            "data": suggestions,
            "count": len(suggestions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predict/{medicine_id}")
def predict_medicine_reorder(
    medicine_id: int,
    days_ahead: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Predict reorder quantity for a specific medicine."""
    try:
        prediction = predict_reorder_quantity(
            db=db,
            medicine_id=medicine_id,
            days_ahead=days_ahead
        )
        return {
            "status": "success",
            "medicine_id": medicine_id,
            "prediction": prediction
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analysis")
def get_reorder_analysis(db: Session = Depends(get_db)):
    """Get detailed reorder analysis and trends."""
    try:
        from sqlalchemy import func
        from datetime import datetime, timedelta
        from ...models.sales import Sale
        from ...models.medicine import Medicine

        # Get top medicines by sales
        top_medicines = db.query(
            Sale.medicine_name,
            func.sum(Sale.quantity).label("total_sold"),
            func.avg(Sale.quantity).label("avg_qty"),
        ).group_by(Sale.medicine_name).order_by(
            func.sum(Sale.quantity).desc()
        ).limit(10).all()

        analysis = {
            "top_sellers": [
                {
                    "name": m.medicine_name,
                    "total_sold": m.total_sold,
                    "avg_per_transaction": float(m.avg_qty or 0),
                }
                for m in top_medicines
            ]
        }
        return {"status": "success", "data": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
