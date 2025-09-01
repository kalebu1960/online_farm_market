""
Test script to verify the database models are properly set up.
Run with: python test_setup.py
"""
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.append('.')

try:
    # Try to import the models
    from online_farm_market.models.base import Base
    from online_farm_market.models.user import User
    from online_farm_market.models.farmer import Farmer
    from online_farm_market.models.product import Product, ProductCategory
    
    print("✅ All required model imports successful!")
    
    # Test database connection
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    
    print("✅ Database tables created successfully!")
    
    # Test creating a user
    db = Session()
    user = User(
        email="test@example.com",
        hashed_password="testpass123",
        full_name="Test User",
        is_active=True
    )
    db.add(user)
    db.commit()
    
    print("✅ User creation successful!")
    
    # Test creating a farmer
    farmer = Farmer(
        farm_name="Test Farm",
        user_id=user.id,
        address="123 Test St",
        city="Testville",
        state="TS",
        zip_code="12345"
    )
    db.add(farmer)
    db.commit()
    
    print("✅ Farmer creation successful!")
    
    # Test creating a product
    product = Product(
        name="Test Product",
        description="A test product",
        price=9.99,
        category=ProductCategory.OTHER,
        farmer_id=farmer.id,
        stock_quantity=10
    )
    db.add(product)
    db.commit()
    
    print("✅ Product creation successful!")
    print("\n🎉 All tests passed! Your models are working correctly.")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nPlease check the following:")
    print("1. All required models are in the models/ directory")
    print("2. All model files have the correct imports")
    print("3. The database URL is correctly configured")
    print("4. All required dependencies are installed")
    sys.exit(1)
