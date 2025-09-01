""
Simple test runner for the Online Farm Market application.
Run with: python run_tests.py
"""
import sys
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.append('.')

try:
    # Import models
    from online_farm_market.models.base import Base
    from online_farm_market.models.user import User
    from online_farm_market.models.farmer import Farmer
    from online_farm_market.models.product import Product, ProductCategory
    
    print("✅ Successfully imported all models")
    
    # Set up test database
    engine = create_engine('sqlite:///:memory:', echo=True)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    db = Session()
    
    print("✅ Test database created successfully")
    
    # Test 1: Create a user
    user = User(
        email="test@example.com",
        hashed_password="hashedpass123",
        full_name="Test User",
        phone_number="1234567890",
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Test 2: Create a farmer
    farmer = Farmer(
        farm_name="Test Farm",
        farm_description="A test farm",
        address="123 Farm Rd",
        city="Farmville",
        state="TS",
        zip_code="12345",
        is_certified_organic=True,
        user_id=user.id,
        delivery_available=True,
        pickup_available=True
    )
    db.add(farmer)
    db.commit()
    
    # Test 3: Create a product
    product = Product(
        name="Organic Apples",
        description="Fresh organic apples",
        price=2.99,
        category=ProductCategory.FRUITS,
        stock_quantity=100,
        unit="kg",
        is_organic=True,
        farmer_id=farmer.id
    )
    db.add(product)
    db.commit()
    
    # Verify the data
    print("\n=== Test Results ===")
    print(f"User created: {user.email}")
    print(f"Farmer created: {farmer.farm_name}")
    print(f"Product created: {product.name} (${product.price:.2f})")
    print("\n✅ All tests passed successfully!")
    
except Exception as e:
    print(f"\n❌ Test failed: {str(e)}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
