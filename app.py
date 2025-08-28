# minimal app.py to test models import
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import User, Farmer, Product, Customer, Transaction

# -------------------- DATABASE SETUP --------------------
DATABASE_URL = "sqlite:///farm_market.db"  # or your preferred DB

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Create tables if they don't exist
Base.metadata.create_all(engine)

# -------------------- EXAMPLE USAGE --------------------
def main():
    # Example: Create a new user
    user_id = User.create(db, username="caleb", email="caleb@example.com")
    print(f"New User ID: {user_id}")

    # Example: List all users
    users = User.get_all(db)
    print("All users:", users)

    # Example: Create a new farmer
    farmer_id = Farmer.create(db, name="John Doe", location="Nairobi")
    print(f"New Farmer ID: {farmer_id}")

    # Example: Create a product
    product_id = Product.create(db, name="Tomatoes", price=100.0, farmer_id=farmer_id)
    print(f"New Product ID: {product_id}")

    # Example: Create a customer
    customer_id = Customer.create(db, name="Alice", email="alice@example.com")
    print(f"New Customer ID: {customer_id}")

    # Example: Create a transaction
    transaction_id = Transaction.create(db, customer_id=customer_id, product_id=product_id, quantity=5)
    print(f"New Transaction ID: {transaction_id}")

if _name_ == "_main_":
    main()