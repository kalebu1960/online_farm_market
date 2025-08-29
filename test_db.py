import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, User, Farmer, Product, Customer, Transaction, TransactionItem

# Create an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///test_farm_market.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_data():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    db = TestingSessionLocal()
    
    try:
        # Create a test user
        test_user = User(
            email="test@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
            full_name="Test User",
            phone_number="+1234567890",
            role="customer",
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create a test customer
        test_customer = Customer(
            user_id=test_user.id,
            shipping_address="123 Test St",
            city="Testville",
            state="TS",
            zip_code="12345"
        )
        db.add(test_customer)
        
        # Create a test farmer
        test_farmer_user = User(
            email="farmer@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
            full_name="Test Farmer",
            phone_number="+1987654321",
            role="farmer",
            is_active=True
        )
        db.add(test_farmer_user)
        db.commit()
        db.refresh(test_farmer_user)
        
        test_farmer = Farmer(
            user_id=test_farmer_user.id,
            farm_name="Test Farm",
            bio="We grow the best test vegetables!",
            address="456 Farm Rd",
            city="Farmville",
            state="FV",
            zip_code="54321"
        )
        db.add(test_farmer)
        db.commit()
        
        # Create a test product
        test_product = Product(
            name="Test Carrots",
            description="Fresh organic carrots",
            price=2.99,
            category="vegetables",
            quantity_available=100,
            unit="lb",
            is_organic=True,
            farmer_id=test_farmer.id
        )
        db.add(test_product)
        db.commit()
        
        # Create a test transaction
        test_transaction = Transaction(
            customer_id=test_customer.id,
            user_id=test_user.id,
            total_amount=5.98,
            status="paid",  # Using the correct enum value
            shipping_address=test_customer.shipping_address,
            payment_method="credit_card",
            payment_status="paid"
        )
        db.add(test_transaction)
        db.commit()
        
        # Create a test transaction item
        test_item = TransactionItem(
            transaction_id=test_transaction.id,
            product_id=test_product.id,
            quantity=2,
            price_per_unit=test_product.price
        )
        db.add(test_item)
        db.commit()
        
        print("✅ Test data created successfully!")
        print(f"- User: {test_user.email}")
        print(f"- Customer: {test_customer.id}")
        print(f"- Farmer: {test_farmer.farm_name}")
        print(f"- Product: {test_product.name} (${test_product.price})")
        print(f"- Transaction: #{test_transaction.id} (${test_transaction.total_amount})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def query_test_data():
    db = TestingSessionLocal()
    try:
        # Query all users
        users = db.query(User).all()
        print("\n📋 Users:")
        for user in users:
            print(f"- {user.email} ({user.role})")
        
        # Query all farmers and their products
        farmers = db.query(Farmer).all()
        print("\n🌱 Farmers:")
        for farmer in farmers:
            products = db.query(Product).filter(Product.farmer_id == farmer.id).all()
            print(f"- {farmer.farm_name} ({len(products)} products)")
            for product in products:
                print(f"  - {product.name}: ${product.price} ({product.quantity_available} {product.unit} available)")
        
        # Query all transactions
        transactions = db.query(Transaction).all()
        print("\n💳 Transactions:")
        for tx in transactions:
            customer = db.query(Customer).filter(Customer.id == tx.customer_id).first()
            user = db.query(User).filter(User.id == tx.user_id).first()
            items = db.query(TransactionItem).filter(TransactionItem.transaction_id == tx.id).all()
            
            print(f"- Transaction #{tx.id}: ${tx.total_amount} ({tx.status})")
            print(f"  Customer: {user.full_name}")
            print(f"  Items ({len(items)}):")
            for item in items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                print(f"  - {item.quantity}x {product.name} @ ${item.price_per_unit}/ea")
        
        return True
        
    except Exception as e:
        print(f"❌ Error querying test data: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Testing database setup...")
    
    # Reset test database
    Base.metadata.drop_all(bind=engine)
    
    # Create test data
    if create_test_data():
        # Query and display test data
        query_test_data()
    
    print("\n✅ Database test completed!")
