"""
Test the core farmer and product functionality of the Online Farm Market.

These tests verify that:
1. Farmers can be created and managed
2. Products can be added and updated
3. Farmers can be searched with various filters
4. Product listings work as expected
"""
import pytest
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import models
from online_farm_market.models.base import Base
from online_farm_market.models.user import User
from online_farm_market.models.farmer import Farmer
from online_farm_market.models.product import Product, ProductCategory

# Test database setup
@pytest.fixture(scope="module")
def test_db():
    # Create an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a test session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# Test data
@pytest.fixture
def sample_user(test_db):
    # Generate a unique email for each test run
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    user = User(
        email=unique_email,
        hashed_password="hashedpassword123",
        full_name="Test User",
        phone_number="1234567890",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def sample_farmer(test_db, sample_user):
    farmer = Farmer(
        farm_name="Test Farm",
        farm_description="A test farm",
        address="123 Farm Rd",
        city="Farmville",
        state="Test State",
        zip_code="12345",
        website="https://testfarm.com",
        user_id=sample_user.id
    )
    test_db.add(farmer)
    test_db.commit()
    test_db.refresh(farmer)
    return farmer

# Tests
def test_farmer_creation(sample_farmer):
    """Test that a farmer can be created with all required fields."""
    assert sample_farmer.farm_name == "Test Farm"
    assert sample_farmer.city == "Farmville"
    assert sample_farmer.website == "https://testfarm.com"


def test_add_product_to_farmer(test_db, sample_farmer):
    """Test adding a product to a farmer's inventory."""
    product = Product(
        name="Organic Apples",
        description="Fresh organic apples",
        price=2.99,
        category=ProductCategory.FRUITS,
        stock_quantity=100,
        unit="kg",
        is_organic=True,
        farmer_id=sample_farmer.id,
        images=["apple1.jpg", "apple2.jpg"]
    )
    test_db.add(product)
    test_db.commit()
    
    # Verify the product was added
    assert product.id is not None
    assert product.name == "Organic Apples"
    assert product.farmer_id == sample_farmer.id
    assert product.is_available is True


def test_search_farmers(test_db, sample_user):
    """Test searching for farmers with various filters."""
    # Clear any existing data to ensure test isolation
    test_db.query(Product).delete()
    test_db.query(Farmer).delete()
    test_db.commit()
    
    # Create a fresh farmer for this test
    farmer = Farmer(
        user_id=sample_user.id,
        farm_name="Test Farm",
        farm_description="A test farm",
        address="123 Farm Rd",
        city="Farmville",
        state="Test State",
        zip_code="12345",
        website="https://testfarm.com"
    )
    test_db.add(farmer)
    test_db.commit()
    
    # Search by city
    farmers, total = Farmer.search_farmers(test_db, city="Farmville")
    assert total == 1
    assert farmers[0].id == farmer.id
    
    # Search by state
    farmers, total = Farmer.search_farmers(test_db, state="Test State")
    assert total == 1
    assert farmers[0].id == farmer.id
    
    # Search by both city and state
    farmers, total = Farmer.search_farmers(test_db, city="Farmville", state="Test State")
    assert total == 1
    assert farmers[0].id == farmer.id


def test_product_availability(test_db, sample_farmer):
    """Test product availability and stock management."""
    # Add a product with limited stock
    product = Product(
        name="Limited Eggs",
        description="Farm fresh eggs",
        price=4.99,
        category=ProductCategory.DAIRY,
        stock_quantity=12,
        unit="dozen",
        farmer_id=sample_farmer.id
    )
    test_db.add(product)
    test_db.commit()
    
    # Check initial availability
    assert product.is_available is True
    assert product.available_quantity == 12.0
    
    # Update stock
    product.stock_quantity = 0
    test_db.commit()
    
    # Verify product is marked as unavailable
    assert product.is_available is False
    assert product.available_quantity == 0.0


def test_farmer_contact_info(sample_farmer, sample_user):
    """Test that farmer contact information is correctly retrieved."""
    assert sample_farmer.farm_name == "Test Farm"
    assert sample_farmer.website == "https://testfarm.com"
    assert sample_farmer.city == "Farmville"
    assert sample_farmer.state == "Test State"


if __name__ == "__main__":
    # This allows running the tests directly with Python for debugging
    import sys
    pytest.main(sys.argv)
