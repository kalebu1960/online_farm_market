from flask import Flask, jsonify, request, g
from database import (
    get_db, init_db, User, Farmer, Product, Customer, Transaction,
    UserRole, TransactionStatus
)
from functools import wraps
from sqlalchemy.orm import Session
import hashlib
import os
from typing import Generator

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')

# Database session management
def get_db_session() -> Generator[Session, None, None]:
    if 'db' not in g:
        g.db = next(get_db())
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Helper functions
def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    return stored_password == hash_password(provided_password)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add your authentication logic here
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Online Farm Market API!"})

# User Routes
@app.route('/users', methods=['GET'])
@login_required
def get_users():
    db = get_db_session()
    users = User.get_all(db)
    return jsonify([
        {"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role.value}
        for u in users
    ])

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    db = get_db_session()
    
    # Validate required fields
    required_fields = ['email', 'password', 'full_name']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        # Check if user already exists
        if User.get_by_email(db, data['email']):
            return jsonify({"error": "Email already registered"}), 400
            
        # Create user
        user = User.create(
            db=db,
            email=data['email'],
            hashed_password=hash_password(data['password']),
            full_name=data['full_name'],
            role=UserRole(data.get('role', UserRole.CUSTOMER.value)),
            phone_number=data.get('phone_number')
        )
        
        # Create customer profile if role is customer
        if user.role == UserRole.CUSTOMER:
            Customer.create(
                db=db,
                user_id=user.id,
                shipping_address=data.get('shipping_address', '')
            )
        
        return jsonify({
            "message": "User created successfully",
            "user_id": user.id,
            "role": user.role.value
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400

# Product Routes
@app.route('/products', methods=['GET'])
def get_products():
    db = get_db_session()
    products = Product.get_available_products(db)
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": float(p.price),
        "quantity_available": p.quantity_available,
        "farmer_id": p.farmer_id,
        "unit": p.unit,
        "category": p.category,
        "is_organic": p.is_organic
    } for p in products])

@app.route('/products', methods=['POST'])
@login_required
def create_product():
    data = request.json
    db = get_db_session()
    
    # Validate required fields
    required_fields = ['name', 'price', 'farmer_id']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        # Create product
        product = Product.create(
            db=db,
            name=data['name'],
            description=data.get('description', ''),
            price=data['price'],
            quantity_available=data.get('quantity_available', 0),
            unit=data.get('unit', 'piece'),
            category=data.get('category', 'other'),
            is_organic=data.get('is_organic', False),
            farmer_id=data['farmer_id']
        )
        
        return jsonify({
            "message": "Product created successfully",
            "product_id": product.id
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400

# Initialize the database
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
