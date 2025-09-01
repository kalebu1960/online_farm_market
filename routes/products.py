from flask import Blueprint, request, jsonify
from ..app import get_db_session, login_required
from ..models import Product, UserRole
from sqlalchemy.orm import Session

# Get the products blueprint from __init__.py
from . import products_bp

@products_bp.route('', methods=['GET'])
def get_products():
    db = get_db_session()
    products = db.query(Product).all()
    
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'description': p.description,
        'price': float(p.price) if p.price else None,
        'quantity': p.quantity,
        'category': p.category,
        'farmer_id': p.farmer_id,
        'created_at': p.created_at.isoformat() if p.created_at else None
    } for p in products])

@products_bp.route('', methods=['POST'])
@login_required
def create_product():
    data = request.get_json()
    db = get_db_session()
    
    # In a real app, you would get the current user from the auth token
    # For now, we'll use a default farmer_id
    farmer_id = data.get('farmer_id')
    
    try:
        product = Product(
            title=data['title'],
            description=data.get('description', ''),
            price=float(data['price']),
            quantity=data.get('quantity', '1'),
            category=data.get('category', 'Other'),
            farmer_id=farmer_id
        )
        
        db.add(product)
        db.commit()
        
        return jsonify({
            "message": "Product created successfully",
            "product_id": product.id
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    db = get_db_session()
    product = db.query(Product).get(product_id)
    
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify({
        'id': product.id,
        'title': product.title,
        'description': product.description,
        'price': float(product.price) if product.price else None,
        'quantity': product.quantity,
        'category': product.category,
        'farmer_id': product.farmer_id,
        'created_at': product.created_at.isoformat() if product.created_at else None
    })
