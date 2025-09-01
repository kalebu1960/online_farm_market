from flask import Blueprint, request, jsonify
from ..app import get_db_session, hash_password
from ..models import User, UserRole
from sqlalchemy.orm import Session
from functools import wraps

# Get the auth blueprint from __init__.py
from . import auth_bp

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add your authentication logic here
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    db = get_db_session()
    
    # Validate required fields
    required_fields = ['email', 'password', 'full_name', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if user already exists
    if db.query(User).filter(User.email == data['email']).first():
        return jsonify({"error": "Email already registered"}), 400
    
    try:
        # Create new user
        user = User(
            email=data['email'],
            hashed_password=hash_password(data['password']),
            full_name=data['full_name'],
            role=UserRole(data['role']),
            phone_number=data.get('phone_number')
        )
        
        db.add(user)
        db.commit()
        
        return jsonify({
            "message": "User registered successfully",
            "user_id": user.id
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db_session()
    
    user = db.query(User).filter(User.email == data.get('email')).first()
    
    if not user or user.hashed_password != hash_password(data.get('password', '')):
        return jsonify({"error": "Invalid email or password"}), 401
    
    # In a real app, you would generate a token here
    return jsonify({
        "message": "Login successful",
        "user_id": user.id,
        "role": user.role.value
    })
