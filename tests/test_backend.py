"""
Test suite for PharmaRec AI Backend
Run with: pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app.config import settings

# Create in-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """Create a test client."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# Auth Tests
def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user(client, db):
    """Test user registration."""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"


def test_login_user(client, db):
    """Test user login."""
    # Register first
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )

    # Login
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# Inventory Tests
def test_create_medicine(client, db):
    """Test creating a medicine."""
    response = client.post(
        "/inventory/",
        json={
            "name": "Paracetamol",
            "generic_name": "Acetaminophen",
            "batch_no": "BATCH001",
            "stock_qty": 100,
            "reorder_level": 10,
            "price": 5.0
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Paracetamol"
    assert data["stock_qty"] == 100


def test_get_medicines(client, db):
    """Test fetching all medicines."""
    # Create some medicines
    for i in range(3):
        client.post(
            "/inventory/",
            json={
                "name": f"Medicine {i}",
                "batch_no": f"BATCH{i}",
                "stock_qty": 50,
                "reorder_level": 10,
                "price": 5.0
            }
        )

    response = client.get("/inventory/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_search_medicines(client, db):
    """Test searching medicines."""
    # Create medicines
    client.post(
        "/inventory/",
        json={
            "name": "Aspirin",
            "batch_no": "B1",
            "stock_qty": 50,
            "reorder_level": 10,
            "price": 2.0
        }
    )

    response = client.get("/inventory/search?q=Aspirin")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Aspirin"


def test_get_low_stock_medicines(client, db):
    """Test getting low stock medicines."""
    # Create medicine with low stock
    client.post(
        "/inventory/",
        json={
            "name": "Low Stock Medicine",
            "batch_no": "B1",
            "stock_qty": 5,
            "reorder_level": 10,
            "price": 5.0
        }
    )

    response = client.get("/inventory/low-stock")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Low Stock Medicine"


# Sales Tests
def test_record_sale(client, db):
    """Test recording a sale."""
    response = client.post(
        "/sales/",
        json={
            "medicine_name": "Paracetamol",
            "quantity": 10,
            "unit_price": 5.0
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["medicine_name"] == "Paracetamol"
    assert data["quantity"] == 10
    assert data["total_amount"] == 50.0


def test_get_sales(client, db):
    """Test fetching sales."""
    # Record some sales
    for i in range(3):
        client.post(
            "/sales/",
            json={
                "medicine_name": f"Medicine {i}",
                "quantity": 10,
                "unit_price": 5.0
            }
        )

    response = client.get("/sales/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_get_sales_summary(client, db):
    """Test getting sales summary."""
    # Record sales for same medicine
    for _ in range(3):
        client.post(
            "/sales/",
            json={
                "medicine_name": "Paracetamol",
                "quantity": 10,
                "unit_price": 5.0
            }
        )

    response = client.get("/sales/summary")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    summary = data[0]
    assert summary["medicine_name"] == "Paracetamol"
    assert summary["total_quantity"] == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
