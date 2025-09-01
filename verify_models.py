""
A simple script to verify the core functionality of the Farmer and Product models.
Run this with: python verify_models.py
"""
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.append('.')

# Import models
from online_farm_market.models.base import Base
from online_farm_market.models.user import User
from online_farm_market.models.farmer import Farmer
from online_farm_market.models.product import Product, ProductCategory

def setup_database():
    """Set up an in-memory SQLite database for testing."""
    engine = create_engine('sqlite:///:memory:', echo=True)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return Session()

def test_farmer_creation():
    """Test creating a farmer and basic properties."""
    print("\n=== Testing Farmer Creation ===")
    db = setup_database()
    
    # Create a test user
    user = User(
        email="test@example.com",
        hashed_password="hashedpass123",
        full_name="Test User",
        phone_number="1234567890",
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Create a farmer
    farmer = Farmer(
        farm_name="Test Farm",
        farm_description="A test farm",
        address="123 Farm Rd",
        city="Farmville",
        state="Test State",
        zip_code="12345",
        is_certified_organic=True,
        user_id=user.id,
        delivery_available=True,
        pickup_available=True
    )
    db.add(farmer)
    db.commit()
    
    # Test basic properties
    assert farmer.farm_name == "Test Farm"
    assert farmer.full_address == "123 Farm Rd, Farmville, Test State 12345"
    
    print("✅ Farmer creation test passed!")
    return db, user, farmer

def test_product_management():
    """Test adding products to a farmer's inventory."""
    print("\n=== Testing Product Management ===")
    db, user, farmer = test_farmer_creation()
    
    # Add a product
    product = Product(
        name="Organic Apples",
        description="Fresh organic apples",
        price=2.99,
        category=ProductCategory.FRUITS,
        stock_quantity=100,
        unit="kg",
        is_organic=True,
        farmer_id=farmer.id,
        images=["apple1.jpg"]
    )
    db.add(product)
    db.commit()
    
    # Test product properties
    assert product.name == "Organic Apples"
    assert product.is_available is True
    
    # Test farmer's products
    farmer_products = farmer.products
    assert len(farmer_products) == 1
    assert farmer_products[0].name == "Organic Apples"
    
    print("✅ Product management test passed!")
    return db, farmer, product

def test_search_functionality():
    """Test searching for farmers and products."""
    print("\n=== Testing Search Functionality ===")
    db, farmer, product = test_product_management()
    
    # Test searching for farmers
    farmers, total = Farmer.search_farmers(db, city="Farmville")
    assert total == 1
    assert farmers[0].farm_name == "Test Farm"
    
    # Test product search
    products = farmer.get_available_products(db)
    assert len(products) == 1
    assert products[0]["name"] == "Organic Apples"
    
    print("✅ Search functionality test passed!")

def main():
    """Run all tests."""
    try:
        test_search_functionality()
        print("\n🎉 All tests passed successfully!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
