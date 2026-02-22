"""
Inventory management routes for medicines.
Provides CRUD operations for medicine inventory with comprehensive validation and error handling.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from datetime import datetime, timedelta
from typing import List

from ...database import get_db
from ...models.medicine import Medicine
from ...schemas.medicine import MedicineCreate, MedicineResponse, MedicineUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/", response_model=List[MedicineResponse])
def get_medicines(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db)
) -> List[MedicineResponse]:
    """
    Get all medicines with pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return, max 1000 (default: 100)
    """
    try:
        medicines = db.query(Medicine).offset(skip).limit(limit).all()
        logger.debug(f"Retrieved {len(medicines)} medicines (skip={skip}, limit={limit})")
        return medicines
    except Exception as e:
        logger.error(f"Error fetching medicines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch medicines"
        )


@router.get("/search", response_model=List[MedicineResponse])
def search_medicines(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    db: Session = Depends(get_db)
) -> List[MedicineResponse]:
    """
    Search medicines by name or generic name.
    
    - **q**: Search query (required, min 1 char, max 100 chars)
    """
    try:
        query = q.strip().lower()
        medicines = db.query(Medicine).filter(
            or_(
                Medicine.name.ilike(f"%{query}%"),
                Medicine.generic_name.ilike(f"%{query}%")
            )
        ).all()
        logger.info(f"Search query '{query}' found {len(medicines)} results")
        return medicines
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search operation failed"
        )


@router.get("/expiring", response_model=List[MedicineResponse])
def get_expiring_medicines(
    days: int = Query(30, ge=1, le=365, description="Days until expiry"),
    db: Session = Depends(get_db)
) -> List[MedicineResponse]:
    """
    Get medicines expiring within specified number of days.
    
    - **days**: Number of days to look ahead (default: 30, min: 1, max: 365)
    """
    try:
        now = datetime.utcnow()
        future_date = now + timedelta(days=days)
        
        medicines = db.query(Medicine).filter(
            Medicine.expiry_date.isnot(None),
            Medicine.expiry_date <= future_date,
            Medicine.expiry_date > now
        ).order_by(Medicine.expiry_date).all()
        
        logger.info(f"Found {len(medicines)} medicines expiring within {days} days")
        return medicines
    except Exception as e:
        logger.error(f"Error fetching expiring medicines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch expiring medicines"
        )


@router.get("/low-stock", response_model=List[MedicineResponse])
def get_low_stock_medicines(db: Session = Depends(get_db)) -> List[MedicineResponse]:
    """
    Get medicines with stock below reorder level.
    Useful for inventory replenishment alerts.
    """
    try:
        medicines = db.query(Medicine).filter(
            Medicine.stock_qty <= Medicine.reorder_level
        ).order_by(Medicine.stock_qty).all()
        
        logger.info(f"Found {len(medicines)} medicines with low stock")
        return medicines
    except Exception as e:
        logger.error(f"Error fetching low stock medicines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch low stock medicines"
        )


@router.get("/{medicine_id}", response_model=MedicineResponse)
def get_medicine(
    medicine_id: int = Query(..., gt=0, description="Medicine ID"),
    db: Session = Depends(get_db)
) -> MedicineResponse:
    """Get a specific medicine by ID."""
    try:
        medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not medicine:
            logger.warning(f"Medicine not found: ID {medicine_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medicine with ID {medicine_id} not found"
            )
        return medicine
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching medicine {medicine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch medicine"
        )


@router.post("/", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
def create_medicine(
    medicine: MedicineCreate,
    db: Session = Depends(get_db)
) -> MedicineResponse:
    """
    Create a new medicine entry.
    
    Validates all input fields including price, stock quantity, and expiry date.
    """
    try:
        # Check if medicine with same batch already exists
        existing = db.query(Medicine).filter(
            Medicine.name == medicine.name,
            Medicine.batch_no == medicine.batch_no
        ).first()
        
        if existing:
            logger.warning(f"Duplicate medicine: {medicine.name} ({medicine.batch_no})")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Medicine '{medicine.name}' with batch '{medicine.batch_no}' already exists"
            )
        
        db_medicine = Medicine(**medicine.dict())
        db.add(db_medicine)
        db.commit()
        db.refresh(db_medicine)
        
        logger.info(f"Created medicine: {db_medicine.name} (ID: {db_medicine.id})")
        return db_medicine
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating medicine: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create medicine"
        )


@router.put("/{medicine_id}", response_model=MedicineResponse)
def update_medicine(
    medicine_id: int = Query(..., gt=0, description="Medicine ID"),
    medicine_update: MedicineUpdate = None,
    db: Session = Depends(get_db)
) -> MedicineResponse:
    """
    Update a medicine entry.
    
    Only provided fields will be updated (partial update support).
    """
    try:
        db_medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not db_medicine:
            logger.warning(f"Medicine not found for update: ID {medicine_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medicine with ID {medicine_id} not found"
            )

        update_data = medicine_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_medicine, key, value)

        db_medicine.updated_at = datetime.utcnow()
        db.add(db_medicine)
        db.commit()
        db.refresh(db_medicine)
        
        logger.info(f"Updated medicine: ID {medicine_id}")
        return db_medicine
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating medicine {medicine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update medicine"
        )


@router.delete("/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medicine(
    medicine_id: int = Query(..., gt=0, description="Medicine ID"),
    db: Session = Depends(get_db)
) -> None:
    """Delete a medicine entry (soft delete recommended for production)."""
    try:
        db_medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not db_medicine:
            logger.warning(f"Medicine not found for deletion: ID {medicine_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medicine with ID {medicine_id} not found"
            )
        
        db.delete(db_medicine)
        db.commit()
        logger.info(f"Deleted medicine: ID {medicine_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting medicine {medicine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete medicine"
        )

    db.delete(db_medicine)
    db.commit()
    return None
