#!/usr/bin/env python3
"""
Database seeding script for PharmaRec AI.
Creates sample data for testing and demonstration.
Run: python scripts/seed_db.py
"""
from backend.app.database import SessionLocal, init_db
from backend.app.models.medicine import Medicine
from backend.app.models.sales import Sale
from backend.app.models.users import User
from backend.app.api.routes.auth import hash_password
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database():
    """Seed database with sample data."""
    # Initialize database
    init_db()
    db = SessionLocal()

    try:
        # Create test user
        test_user = User(
            email="demo@pharmacy.com",
            password_hash=hash_password("demo123456"),
            full_name="Demo Pharmacy",
            is_active=True
        )
        db.add(test_user)
        logger.info("✅ Created demo user: demo@pharmacy.com")

        # Create sample medicines
        medicines = [
            Medicine(
                name="Paracetamol 500mg",
                generic_name="Acetaminophen",
                batch_no="BATCH001",
                expiry_date=datetime.utcnow() + timedelta(days=180),
                stock_qty=100,
                reorder_level=10,
                price=5.0,
                manufacturer="Generic Pharma"
            ),
            Medicine(
                name="Ibuprofen 200mg",
                generic_name="Ibuprofen",
                batch_no="BATCH002",
                expiry_date=datetime.utcnow() + timedelta(days=200),
                stock_qty=50,
                reorder_level=15,
                price=3.5,
                manufacturer="Generic Pharma"
            ),
            Medicine(
                name="Aspirin 75mg",
                generic_name="Acetylsalicylic Acid",
                batch_no="BATCH003",
                expiry_date=datetime.utcnow() + timedelta(days=150),
                stock_qty=5,  # Low stock for testing
                reorder_level=20,
                price=2.0,
                manufacturer="Generic Pharma"
            ),
            Medicine(
                name="Metformin 500mg",
                generic_name="Metformin",
                batch_no="BATCH004",
                expiry_date=datetime.utcnow() + timedelta(days=120),
                stock_qty=0,  # Out of stock
                reorder_level=25,
                price=1.5,
                manufacturer="Generic Pharma"
            ),
            Medicine(
                name="Amoxicillin 500mg",
                generic_name="Amoxicillin",
                batch_no="BATCH005",
                expiry_date=datetime.utcnow() + timedelta(days=30),  # Expiring soon
                stock_qty=20,
                reorder_level=10,
                price=8.0,
                manufacturer="Generic Pharma"
            ),
        ]

        for med in medicines:
            db.add(med)
        logger.info(f"✅ Created {len(medicines)} sample medicines")

        # Create sample sales
        base_date = datetime.utcnow()
        sales = []

        for i in range(30):  # 30 days of sales
            date = base_date - timedelta(days=i)

            # Paracetamol - high volume
            for _ in range(3):
                sales.append(Sale(
                    medicine_name="Paracetamol 500mg",
                    quantity=2,
                    unit_price=5.0,
                    total_amount=10.0,
                    sale_date=date
                ))

            # Ibuprofen - medium volume
            for _ in range(2):
                sales.append(Sale(
                    medicine_name="Ibuprofen 200mg",
                    quantity=1,
                    unit_price=3.5,
                    total_amount=3.5,
                    sale_date=date
                ))

            # Aspirin - lower volume
            sales.append(Sale(
                medicine_name="Aspirin 75mg",
                quantity=1,
                unit_price=2.0,
                total_amount=2.0,
                sale_date=date
            ))

        for sale in sales:
            db.add(sale)
        logger.info(f"✅ Created {len(sales)} sample sales records")

        # Commit all
        db.commit()
        logger.info("✅ Database seeded successfully")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding PharmaRec AI database...")
    seed_database()
    print("✅ Done! Login with: demo@pharmacy.com / demo123456")
