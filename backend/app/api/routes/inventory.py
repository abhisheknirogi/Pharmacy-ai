from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from ...database import get_db
from ...models.medicine import Medicine
from ...schemas.medicine import MedicineCreate, MedicineResponse, MedicineUpdate

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/", response_model=list[MedicineResponse])
def get_medicines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all medicines with pagination."""
    medicines = db.query(Medicine).offset(skip).limit(limit).all()
    return medicines


@router.get("/search", response_model=list[MedicineResponse])
def search_medicines(q: str = Query(...), db: Session = Depends(get_db)):
    """Search medicines by name or generic name."""
    medicines = db.query(Medicine).filter(
        (Medicine.name.ilike(f"%{q}%")) | (Medicine.generic_name.ilike(f"%{q}%"))
    ).all()
    return medicines


@router.get("/expiring", response_model=list[MedicineResponse])
def get_expiring_medicines(
    days: int = Query(30, ge=1),
    db: Session = Depends(get_db)
):
    """Get medicines expiring within specified days."""
    future_date = datetime.utcnow() + timedelta(days=days)
    medicines = db.query(Medicine).filter(
        (Medicine.expiry_date <= future_date) & 
        (Medicine.expiry_date > datetime.utcnow())
    ).all()
    return medicines


@router.get("/low-stock", response_model=list[MedicineResponse])
def get_low_stock_medicines(db: Session = Depends(get_db)):
    """Get medicines with low stock."""
    medicines = db.query(Medicine).filter(
        Medicine.stock_qty <= Medicine.reorder_level
    ).all()
    return medicines


@router.get("/{medicine_id}", response_model=MedicineResponse)
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    """Get a specific medicine by ID."""
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine


@router.post("/", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
def create_medicine(medicine: MedicineCreate, db: Session = Depends(get_db)):
    """Add a new medicine."""
    db_medicine = Medicine(**medicine.dict())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine


@router.put("/{medicine_id}", response_model=MedicineResponse)
def update_medicine(
    medicine_id: int,
    medicine_update: MedicineUpdate,
    db: Session = Depends(get_db)
):
    """Update a medicine."""
    db_medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    for key, value in medicine_update.dict(exclude_unset=True).items():
        setattr(db_medicine, key, value)

    db_medicine.updated_at = datetime.utcnow()
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine


@router.delete("/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    """Delete a medicine."""
    db_medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    db.delete(db_medicine)
    db.commit()
    return None
