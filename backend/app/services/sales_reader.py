import pandas as pd
from sqlalchemy.orm import Session
from ..models.sales import Sale
from ..models.medicine import Medicine
import logging

logger = logging.getLogger(__name__)


def process_medivision_sales(db: Session, file_path: str):
    """
    Process Medivision sales file (Excel or CSV).
    Expected columns: Item Name, Qty, Price (optional)
    """
    try:
        # Read file based on extension
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.xls'):
            df = pd.read_excel(file_path, engine='xlrd')
        else:
            df = pd.read_csv(file_path)

        # Map columns - be flexible with column names
        col_mapping = {
            'Item Name': ['Item Name', 'Medicine Name', 'Name', 'Product', 'Item'],
            'Qty': ['Qty', 'Quantity', 'Qte', 'Amount'],
            'Price': ['Price', 'Unit Price', 'Rate', 'Cost']
        }

        # Find actual columns
        columns = df.columns.tolist()
        item_col = None
        qty_col = None
        price_col = None

        for standard, variants in col_mapping.items():
            for col in columns:
                if col in variants:
                    if standard == 'Item Name':
                        item_col = col
                    elif standard == 'Qty':
                        qty_col = col
                    elif standard == 'Price':
                        price_col = col

        if not item_col or not qty_col:
            raise ValueError(f"Required columns not found. Available: {columns}")

        # Process sales
        processed = 0
        for _, row in df.iterrows():
            try:
                medicine_name = str(row[item_col]).strip()
                quantity = int(float(row[qty_col]))
                unit_price = float(row[price_col]) if price_col and pd.notna(row[price_col]) else 0.0
                total_amount = quantity * unit_price if unit_price > 0 else 0.0

                # Find medicine ID if it exists
                medicine = db.query(Medicine).filter(
                    Medicine.name.ilike(medicine_name)
                ).first()

                new_sale = Sale(
                    medicine_id=medicine.id if medicine else None,
                    medicine_name=medicine_name,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_amount=total_amount,
                )
                db.add(new_sale)
                processed += 1

            except Exception as e:
                logger.warning(f"Error processing row: {e}")
                continue

        db.commit()
        logger.info(f"Processed {processed} sales records")
        return processed

    except Exception as e:
        logger.error(f"Error processing sales file: {str(e)}")
        db.rollback()
        raise
