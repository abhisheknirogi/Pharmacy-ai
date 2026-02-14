from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from ..database import get_db
from ...models.sales import Sale
from ...models.medicine import Medicine
from ...schemas.sales import SaleCreate, SaleResponse, SaleSummary
from ...services.sales_reader import process_medivision_sales
import os

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def record_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    """Record a new sale/billing transaction."""
    # Calculate total if not provided
    total = sale.total_amount or (sale.quantity * sale.unit_price)

    # Update medicine stock if ID provided
    if sale.medicine_id:
        medicine = db.query(Medicine).filter(Medicine.id == sale.medicine_id).first()
        if medicine:
            medicine.stock_qty -= sale.quantity
            if medicine.stock_qty < 0:
                medicine.stock_qty = 0

    db_sale = Sale(
        medicine_id=sale.medicine_id,
        medicine_name=sale.medicine_name,
        quantity=sale.quantity,
        unit_price=sale.unit_price,
        total_amount=total,
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.get("/", response_model=list[SaleResponse])
def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    days: int = Query(30, description="Filter sales from last N days"),
    db: Session = Depends(get_db)
):
    """Get sales history with optional filtering."""
    date_limit = datetime.utcnow() - timedelta(days=days)
    sales = db.query(Sale).filter(
        Sale.sale_date >= date_limit
    ).order_by(desc(Sale.sale_date)).offset(skip).limit(limit).all()
    return sales


@router.get("/summary", response_model=list[SaleSummary])
def get_sales_summary(
    days: int = Query(30, description="Summary for last N days"),
    db: Session = Depends(get_db)
):
    """Get summary of sales by medicine."""
    date_limit = datetime.utcnow() - timedelta(days=days)

    summaries = db.query(
        Sale.medicine_name,
        func.sum(Sale.quantity).label("total_quantity"),
        func.sum(Sale.total_amount).label("total_amount"),
        func.count(Sale.id).label("transaction_count"),
    ).filter(Sale.sale_date >= date_limit).group_by(Sale.medicine_name).all()

    return [
        SaleSummary(
            medicine_name=s.medicine_name,
            total_quantity=s.total_quantity or 0,
            total_amount=s.total_amount or 0.0,
            transaction_count=s.transaction_count or 0,
        )
        for s in summaries
    ]


@router.get("/daily-revenue")
def get_daily_revenue(
    days: int = Query(30),
    db: Session = Depends(get_db)
):
    """Get daily revenue for analytics."""
    date_limit = datetime.utcnow() - timedelta(days=days)

    daily_data = db.query(
        func.date(Sale.sale_date).label("date"),
        func.sum(Sale.total_amount).label("revenue"),
        func.count(Sale.id).label("transactions"),
    ).filter(Sale.sale_date >= date_limit).group_by(
        func.date(Sale.sale_date)
    ).all()

    return [
        {
            "date": str(d.date),
            "revenue": float(d.revenue or 0),
            "transactions": d.transactions or 0,
        }
        for d in daily_data
    ]


@router.post("/upload")
async def upload_sales_report(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """Upload sales file (CSV/Excel)."""
    os.makedirs("data/sales", exist_ok=True)

    temp_path = f"data/sales/{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        rows_processed = process_medivision_sales(db, temp_path)
        return {
            "status": "success",
            "message": "File processed",
            "rows_processed": rows_processed
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
