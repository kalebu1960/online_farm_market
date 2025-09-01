import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from online_farm_market.models.base import Base
from online_farm_market.models.user import User, UserRole
from online_farm_market.models.farmer import Farmer
from online_farm_market.models.product import Product, ProductCategory

# Test database setup
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for testing with automatic cleanup."""
    # Drop all tables to ensure a clean state
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    db = TestingSessionLocal()
    
    try:
        # Begin a transaction
        db.begin()
        yield db
        
        # Rollback any changes made during the test
        db.rollback()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        # Close the session
        db.close()
        
        # Clean up tables
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_user():
    """Create a sample user for testing with a unique email."""
    import uuid
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    return User(
        email=unique_email,
        password="testpassword",
        full_name="Test User",
        phone_number="1234567890",
        role=UserRole.FARMER
    )

@pytest.fixture
def sample_farmer(sample_user):
    """Create a sample farmer for testing."""
    return Farmer(
        user=sample_user,
        farm_name="Test Farm",
        farm_description="Test farm description",
        address="123 Farm Road",
        city="Farmville",
        state="CA",
        zip_code="12345"
    )

@pytest.fixture
def sample_product(sample_farmer):
    """Create a sample product for testing."""
    return Product(
        name="Test Product",
        description="Test product description",
        price=9.99,
        category=ProductCategory.VEGETABLES,
        stock_quantity=100,
        unit="kg",
        is_organic=True,
        is_available=True,
        farmer=sample_farmer
    )

def test_user_creation(db_session, sample_user):
    """Test user creation and password hashing."""
    db_session.add(sample_user)
    db_session.commit()
    
    # Test password hashing
    assert sample_user.hashed_password is not None
    assert sample_user.hashed_password != "testpassword"
    assert sample_user.verify_password("testpassword") is True
    assert sample_user.verify_password("wrongpassword") is False
    
    # Test role checks
    assert sample_user.is_farmer() is True
    assert sample_user.is_admin() is False
    assert sample_user.is_customer() is False

def test_farmer_creation(db_session, sample_farmer):
    """Test farmer creation and relationships."""
    db_session.add(sample_farmer)
    db_session.commit()
    
    assert sample_farmer.id is not None
    assert sample_farmer.user.role == UserRole.FARMER
    assert sample_farmer.farm_name == "Test Farm"
    assert sample_farmer.user.full_name == "Test User"

def test_product_creation(db_session, sample_product):
    """Test product creation and relationships."""
    db_session.add(sample_product)
    db_session.commit()
    
    assert sample_product.id is not None
    assert sample_product.name == "Test Product"
    assert sample_product.farmer.farm_name == "Test Farm"
    assert sample_product.category == ProductCategory.VEGETABLES
    assert sample_product.is_available is True
    assert sample_product.stock_quantity == 100
    
    # Test stock update
    sample_product.stock_quantity = 50
    db_session.commit()
    assert sample_product.stock_quantity == 50

def test_product_search(db_session, sample_product):
    """Test product search functionality."""
    db_session.add(sample_product)
    db_session.commit()
    
    # Add another product
    product2 = Product(
        name="Organic Apples",
        description="Fresh organic apples",
        price=4.99,
        category=ProductCategory.FRUITS,
        stock_quantity=50,
        unit="lb",
        is_organic=True,
        is_available=True,
        farmer=sample_product.farmer
    )
    db_session.add(product2)
    db_session.commit()
    
    # Test search by category - should find only the vegetable product
    products = Product.get_available_products(
        db_session,
        category=ProductCategory.VEGETABLES
    ).all()
    assert len(products) == 1
    assert products[0].name == "Test Product"
    
    # Test search by fruits category
    products = Product.get_available_products(
        db_session,
        category=ProductCategory.FRUITS
    ).all()
    assert len(products) == 1
    assert products[0].name == "Organic Apples"
    
    # Test search by organic only
    products = Product.get_available_products(
        db_session,
        organic_only=True
    ).all()
    assert len(products) == 2  # All products are organic
    
    # Test search by text
    products = Product.get_available_products(
        db_session,
        search="apples"
    ).all()
    assert len(products) == 1
    assert products[0].name == "Organic Apples"
