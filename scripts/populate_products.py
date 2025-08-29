"""
Script to populate the database with sample farm products.
Run with: python -m scripts.populate_products
"""
import sys
import os
from datetime import datetime, timedelta
from random import choice, randint, uniform

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from online_farm_market.models.user import User, UserRole
from online_farm_market.models.farmer import Farmer
from online_farm_market.models.product import Product
from online_farm_market.db import SessionLocal, init_db

def create_sample_farmers(db):
    """Create sample farmers in the database."""
    farmers = [
        {
            "email": "organic_farmer@example.com",
            "password": "securepassword123",
            "full_name": "John Farmer",
            "farm_name": "Organic Valley Farm",
            "bio": "Sustainable farming practices since 1995.",
            "address": "123 Farm Road",
            "city": "Springfield",
            "state": "Vermont",
            "zip_code": "12345",
            "phone_number": "(555) 123-4567"
        },
        {
            "email": "berry_farm@example.com",
            "password": "berrysweet456",
            "full_name": "Sarah Berry",
            "farm_name": "Berry Delight Farms",
            "bio": "Specializing in organic berries and honey.",
            "address": "456 Orchard Lane",
            "city": "Portland",
            "state": "Oregon",
            "zip_code": "97201",
            "phone_number": "(555) 234-5678"
        },
        {
            "email": "green_thumb@example.com",
            "password": "growbig789",
            "full_name": "Mike Green",
            "farm_name": "Green Thumb Produce",
            "bio": "Fresh vegetables grown with care.",
            "address": "789 Garden Street",
            "city": "Austin",
            "state": "Texas",
            "zip_code": "73301",
            "phone_number": "(555) 345-6789"
        }
    ]
    
    created_farmers = []
    for farmer_data in farmers:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == farmer_data["email"]).first()
        if existing_user:
            farmer = db.query(Farmer).filter(Farmer.user_id == existing_user.id).first()
            if farmer:
                created_farmers.append(farmer)
                continue
        else:
            # Create user
            user = User.create(
                db=db,
                email=farmer_data["email"],
                password=farmer_data["password"],
                full_name=farmer_data["full_name"],
                role=UserRole.FARMER
            )
            
            # Create farmer profile
            farmer = Farmer(
                user_id=user.id,
                farm_name=farmer_data["farm_name"],
                bio=farmer_data["bio"],
                address=farmer_data["address"],
                city=farmer_data["city"],
                state=farmer_data["state"],
                zip_code=farmer_data["zip_code"],
                phone_number=farmer_data["phone_number"]
            )
            db.add(farmer)
            db.commit()
            db.refresh(farmer)
            created_farmers.append(farmer)
    
    return created_farmers

def create_sample_products(db, farmers):
    """Create sample products in the database."""
    products = [
        {
            "title": "Organic Tomatoes",
            "description": "Fresh, vine-ripened organic tomatoes. Grown without synthetic pesticides.",
            "price": 4.99,
            "quantity": "10 lbs",
            "category": "Vegetables",
            "condition": "new",
            "unit": "lb"
        },
        {
            "title": "Strawberries",
            "description": "Sweet and juicy strawberries, hand-picked daily.",
            "price": 6.99,
            "quantity": "5 pints",
            "category": "Fruits",
            "condition": "new",
            "unit": "pint"
        },
        {
            "title": "Free-Range Eggs",
            "description": "Farm-fresh eggs from free-range chickens.",
            "price": 5.99,
            "quantity": "1 dozen",
            "category": "Eggs",
            "condition": "new",
            "unit": "dozen"
        },
        {
            "title": "Raw Honey",
            "description": "Pure, raw honey from local wildflowers.",
            "price": 12.99,
            "quantity": "16 oz",
            "category": "Honey",
            "condition": "new",
            "unit": "jar"
        },
        {
            "title": "Mixed Salad Greens",
            "description": "Freshly harvested mixed salad greens.",
            "price": 3.99,
            "quantity": "8 oz",
            "category": "Vegetables",
            "condition": "new",
            "unit": "pack"
        },
        {
            "title": "Organic Carrots",
            "description": "Sweet and crunchy organic carrots.",
            "price": 2.99,
            "quantity": "2 lbs",
            "category": "Vegetables",
            "condition": "new",
            "unit": "lb"
        },
        {
            "title": "Blueberries",
            "description": "Fresh, plump blueberries, perfect for baking or snacking.",
            "price": 8.99,
            "quantity": "1 lb",
            "category": "Fruits",
            "condition": "new",
            "unit": "lb"
        },
        {
            "title": "Fresh Basil",
            "description": "Aromatic fresh basil, great for cooking.",
            "price": 2.50,
            "quantity": "1 bunch",
            "category": "Herbs",
            "condition": "new",
            "unit": "bunch"
        }
    ]
    
    created_products = []
    for product_data in products:
        # Randomly assign to a farmer
        farmer = choice(farmers)
        
        # Random creation date within last 30 days
        created_at = datetime.utcnow() - timedelta(days=randint(0, 30))
        
        product = Product(
            farmer_id=farmer.id,
            title=product_data["title"],
            description=product_data["description"],
            price=product_data["price"],
            quantity=product_data["quantity"],
            category=product_data["category"],
            condition=product_data["condition"],
            unit=product_data["unit"],
            location=f"{farmer.city}, {farmer.state}",
            is_negotiable=choice([True, False]),
            status="available",
            views=randint(0, 50),
            created_at=created_at,
            updated_at=created_at
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        created_products.append(product)
    
    return created_products

def main():
    """Main function to populate the database with sample data."""
    print("🌱 Populating database with sample data...")
    
    db = SessionLocal()
    try:
        # Initialize database
        init_db()
        
        # Create sample farmers
        print("👨‍🌾 Creating sample farmers...")
        farmers = create_sample_farmers(db)
        print(f"✅ Created {len(farmers)} farmers")
        
        # Create sample products
        print("🍎 Creating sample products...")
        products = create_sample_products(db, farmers)
        print(f"✅ Created {len(products)} products")
        
        print("\n✨ Database populated successfully!")
        
    except Exception as e:
        print(f"❌ Error populating database: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
