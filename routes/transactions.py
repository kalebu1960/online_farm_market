from flask import Blueprint, request, jsonify
from ..app import get_db_session, login_required
from ..models import Transaction, TransactionItem, TransactionStatus, Product
from sqlalchemy.orm import Session
from datetime import datetime

# Get the transactions blueprint from __init__.py
from . import transactions_bp

@transactions_bp.route('', methods=['POST'])
@login_required
def create_transaction():
    data = request.get_json()
    db = get_db_session()
    
    # In a real app, you would get the current user from the auth token
    customer_id = data.get('customer_id')
    user_id = data.get('user_id')  # The user creating the transaction
    
    if not customer_id or not user_id:
        return jsonify({"error": "Customer ID and User ID are required"}), 400
    
    if 'items' not in data or not isinstance(data['items'], list):
        return jsonify({"error": "Items list is required"}), 400
    
    try:
        # Start a transaction
        transaction = Transaction(
            customer_id=customer_id,
            user_id=user_id,
            status=TransactionStatus.PENDING,
            total_amount=0.0
        )
        
        db.add(transaction)
        db.flush()  # Get the transaction ID
        
        total_amount = 0.0
        
        # Process each item in the transaction
        for item in data['items']:
            product_id = item.get('product_id')
            quantity = float(item.get('quantity', 1))
            
            # Get the product
            product = db.query(Product).get(product_id)
            if not product:
                db.rollback()
                return jsonify({"error": f"Product with ID {product_id} not found"}), 404
            
            # Calculate item total
            item_total = float(product.price) * quantity
            total_amount += item_total
            
            # Create transaction item
            transaction_item = TransactionItem(
                transaction_id=transaction.id,
                product_id=product_id,
                quantity=quantity,
                price_per_unit=float(product.price),
                total_price=item_total
            )
            
            db.add(transaction_item)
        
        # Update transaction total
        transaction.total_amount = total_amount
        transaction.status = TransactionStatus.COMPLETED
        
        db.commit()
        
        return jsonify({
            "message": "Transaction completed successfully",
            "transaction_id": transaction.id,
            "total_amount": total_amount
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400

@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
@login_required
def get_transaction(transaction_id):
    db = get_db_session()
    
    transaction = db.query(Transaction).get(transaction_id)
    
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404
    
    # Get transaction items
    items = db.query(TransactionItem).filter(
        TransactionItem.transaction_id == transaction_id
    ).all()
    
    return jsonify({
        'id': transaction.id,
        'customer_id': transaction.customer_id,
        'user_id': transaction.user_id,
        'total_amount': float(transaction.total_amount) if transaction.total_amount else None,
        'status': transaction.status.value,
        'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
        'items': [{
            'product_id': item.product_id,
            'quantity': float(item.quantity) if item.quantity else None,
            'price_per_unit': float(item.price_per_unit) if item.price_per_unit else None,
            'total_price': float(item.total_price) if item.total_price else None
        } for item in items]
    })
