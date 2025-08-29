"""Transaction models for order processing."""
import enum
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Column, String, Numeric, Integer, ForeignKey, Enum, DateTime, CheckConstraint
)
from sqlalchemy.orm import relationship, Session

from ..db import Base
from .base import BaseModel

class TransactionStatus(str, enum.Enum):
    """Status of a transaction."""
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Transaction(Base, BaseModel):
    """Transaction model representing an order."""
    __tablename__ = "transactions"
    
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    shipping_address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    payment_method = Column(String(50))
    payment_status = Column(String(50))
    notes = Column(String(500))
    
    # Shipping information
    tracking_number = Column(String(100))
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
    items = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint(
            'total_amount >= 0', 
            name='check_transaction_total_amount_positive'
        ),
    )
    
    @classmethod
    def get_by_customer_id(
        cls, 
        db: Session, 
        customer_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List['Transaction']:
        """Get all transactions for a specific customer."""
        return (
            db.query(cls)
            .filter(cls.customer_id == customer_id)
            .order_by(cls.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    @classmethod
    def create_with_items(
        cls,
        db: Session,
        customer_id: int,
        user_id: int,
        items: List[dict],
        **kwargs
    ) -> 'Transaction':
        """Create a new transaction with items."""
        from .product import Product
        
        # Calculate total amount
        total_amount = Decimal('0')
        transaction_items = []
        
        # Start a transaction
        try:
            for item in items:
                product = db.query(Product).get(item['product_id'])
                if not product or product.quantity_available < item['quantity']:
                    raise ValueError(f"Product {item.get('product_id')} not available or insufficient quantity")
                
                # Calculate item total
                item_total = Decimal(str(product.price)) * item['quantity']
                total_amount += item_total
                
                # Create transaction item
                transaction_items.append({
                    'product_id': product.id,
                    'quantity': item['quantity'],
                    'unit_price': product.price,
                    'total_price': item_total
                })
                
                # Update product quantity
                product.quantity_available -= item['quantity']
                db.add(product)
            
            # Create transaction
            transaction = cls.create(
                db,
                customer_id=customer_id,
                user_id=user_id,
                total_amount=total_amount,
                **kwargs
            )
            
            # Add items to transaction
            for item in transaction_items:
                TransactionItem.create(
                    db,
                    transaction_id=transaction.id,
                    **item
                )
            
            db.commit()
            return transaction
            
        except Exception as e:
            db.rollback()
            raise e
    
    def update_status(self, db: Session, status: TransactionStatus) -> None:
        """Update the status of the transaction."""
        self.status = status
        
        # Update timestamps based on status
        now = datetime.utcnow()
        if status == TransactionStatus.SHIPPED and not self.shipped_at:
            self.shipped_at = now
        elif status == TransactionStatus.DELIVERED and not self.delivered_at:
            self.delivered_at = now
            
        db.commit()
        db.refresh(self)
    
    def to_dict(self, include_items: bool = True) -> dict:
        """Convert transaction to dictionary."""
        data = super().to_dict()
        data.update({
            'customer_id': self.customer_id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount) if self.total_amount is not None else None,
            'status': self.status.value,
            'shipping_address': self.shipping_address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'notes': self.notes,
            'tracking_number': self.tracking_number,
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
        })
        
        # Include related objects if needed
        if include_items and self.items:
            data['items'] = [item.to_dict() for item in self.items]
            
        if hasattr(self, 'customer') and self.customer:
            data['customer'] = self.customer.to_dict()
            
        if hasattr(self, 'user') and self.user:
            data['user'] = {
                'id': self.user.id,
                'full_name': self.user.full_name,
                'email': self.user.email
            }
            
        return data

class TransactionItem(Base, BaseModel):
    """Transaction item model representing products in a transaction."""
    __tablename__ = "transaction_items"
    
    transaction_id = Column(Integer, ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product", back_populates="transaction_items")
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('unit_price >= 0', name='check_unit_price_positive'),
        CheckConstraint('total_price >= 0', name='check_total_price_positive'),
    )
    
    @classmethod
    def create(
        cls, 
        db: Session, 
        transaction_id: int,
        product_id: int,
        quantity: int,
        unit_price: float,
        **kwargs
    ) -> 'TransactionItem':
        """Create a new transaction item with calculated total price."""
        # Calculate total_price
        total_price = Decimal(str(unit_price)) * quantity
        
        # Create the instance using BaseModel.create
        return super().create(
            db=db,
            transaction_id=transaction_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            **{k: v for k, v in kwargs.items() if k not in ['transaction_id', 'product_id', 'quantity', 'unit_price', 'total_price']}
        )
    
    def to_dict(self) -> dict:
        """Convert transaction item to dictionary."""
        data = super().to_dict()
        data.update({
            'transaction_id': self.transaction_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price is not None else None,
            'total_price': float(self.total_price) if self.total_price is not None else None,
        })
        
        # Include product information if available
        if hasattr(self, 'product') and self.product:
            data['product'] = {
                'id': self.product.id,
                'name': self.product.name,
                'description': self.product.description,
                'unit': self.product.unit,
            }
            
        return data
