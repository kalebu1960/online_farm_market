import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Base, User, Farmer, Product, Customer, Transaction, TransactionItem, UserRole, TransactionStatus
from database import SessionLocal, engine

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_farm_market.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create test database tables
Base.metadata.create_all(bind=test_engine)

def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fixtures
@pytest.fixture(scope="function")
def db_session():
    # Create the database and the database table(s).
    Base.metadata.create_all(test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    # Clean up the database after the test
    Base.metadata.drop_all(test_engine)

# Test cases
def test_user_creation(db_session):
    # Test creating a user
    user_data = {
        "email": "test@example.com",
        "hashed_password": "hashed_password_123",
        "full_name": "Test User",
        "phone_number": "1234567890",
        "role": UserRole.CUSTOMER
    }
    user = User.create(db_session, **user_data)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == UserRole.CUSTOMER
    assert user.is_active is True

def test_farmer_creation(db_session):
    # First create a user
    user = User.create(
        db_session,
        email="farmer@example.com",
        hashed_password="hashed_password_123",
        full_name="Farmer Joe",
        role=UserRole.FARMER
    )
    
    # Then create a farmer
    farmer_data = {
        "user_id": user.id,
        "farm_name": "Joe's Organic Farm",
        "bio": "Organic farming since 2010",
        "address": "123 Farm Rd",
        "city": "Farmville",
        "state": "CA",
        "zip_code": "12345"
    }
    farmer = Farmer.create(db_session, **farmer_data)
    
    assert farmer.id is not None
    assert farmer.farm_name == "Joe's Organic Farm"
    assert farmer.user_id == user.id

def test_product_creation(db_session):
    # Create user and farmer first
    user = User.create(
        db_session,
        email="farmer2@example.com",
        hashed_password="hashed_password_123",
        full_name="Farmer Jane",
        role=UserRole.FARMER
    )
    
    farmer = Farmer.create(
        db_session,
        user_id=user.id,
        farm_name="Jane's Organic Farm"
    )
    
    # Create a product
    product_data = {
        "name": "Organic Tomatoes",
        "description": "Fresh organic tomatoes",
        "price": 2.99,
        "quantity_available": 50,
        "unit": "kg",
        "category": "vegetable",
        "is_organic": True,
        "farmer_id": farmer.id
    }
    product = Product.create(db_session, **product_data)
    
    assert product.id is not None
    assert product.name == "Organic Tomatoes"
    assert float(product.price) == 2.99  # Convert Decimal to float for comparison
    assert product.farmer_id == farmer.id

def test_customer_creation(db_session):
    # Create a user
    user = User.create(
        db_session,
        email="customer@example.com",
        hashed_password="hashed_password_123",
        full_name="John Customer",
        role=UserRole.CUSTOMER
    )
    
    # Create a customer
    customer_data = {
        "user_id": user.id,
        "shipping_address": "123 Customer St",
        "city": "Customerville",
        "state": "NY",
        "zip_code": "10001"
    }
    customer = Customer.create(db_session, **customer_data)
    
    assert customer.id is not None
    assert customer.user_id == user.id
    assert customer.city == "Customerville"

def test_transaction_flow(db_session):
    # Create a farmer and a product
    user_farmer = User.create(
        db_session,
        email="farmer3@example.com",
        hashed_password="hashed_password_123",
        full_name="Farmer Bob",
        role=UserRole.FARMER
    )
    
    farmer = Farmer.create(
        db_session,
        user_id=user_farmer.id,
        farm_name="Bob's Farm"
    )
    
    product = Product.create(
        db_session,
        name="Organic Apples",
        description="Fresh organic apples",
        price=3.50,
        quantity_available=100,
        unit="kg",
        category="fruit",
        is_organic=True,
        farmer_id=farmer.id
    )
    
    # Create a customer
    user_customer = User.create(
        db_session,
        email="customer2@example.com",
        hashed_password="hashed_password_123",
        full_name="Alice Customer",
        role=UserRole.CUSTOMER
    )
    
    customer = Customer.create(
        db_session,
        user_id=user_customer.id,
        shipping_address="456 Customer Ave"
    )
    
    # Create a transaction
    transaction = Transaction.create(
        db_session,
        customer_id=customer.id,
        user_id=user_customer.id,  # Add user_id
        total_amount=10.50,
        status=TransactionStatus.PENDING,
        payment_method="credit_card",
        payment_status="pending"
    )
    
    # Add items to the transaction
    transaction_item = TransactionItem.create(
        db_session,
        transaction_id=transaction.id,
        product_id=product.id,
        quantity=3,
        unit_price=3.50
    )
    
    assert transaction.id is not None
    assert transaction.customer_id == customer.id
    assert transaction.status == TransactionStatus.PENDING
    assert transaction_item.transaction_id == transaction.id
    assert transaction_item.product_id == product.id
    assert transaction_item.quantity == 3
