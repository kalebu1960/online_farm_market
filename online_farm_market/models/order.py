from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey, DateTime, Enum as SQLEnum, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base

class OrderStatus(str, Enum):
    """Order status values."""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Order(Base):
    """Order model for customer purchases."""
    
    __tablename__ = "orders"
    
    # Customer information
    customer_id = Column(ForeignKey('customers.id'), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    
    # Shipping information
    shipping_address = Column(Text, nullable=False)
    shipping_city = Column(String(100), nullable=False)
    shipping_state = Column(String(100), nullable=False)
    shipping_zip_code = Column(String(20), nullable=False)
    
    # Payment information
    payment_method = Column(String(50), nullable=False)  # e.g., 'credit_card', 'paypal', 'cash_on_delivery'
    payment_status = Column(String(20), default='pending', nullable=False)  # 'pending', 'completed', 'failed', 'refunded'
    transaction_id = Column(String(100), nullable=True)  # For payment processor reference
    
    # Totals
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    shipping_cost = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __str__(self):
        return f"Order #{self.id} - {self.status} (${self.total_amount:.2f})"
    
    def update_status(self, db, new_status: OrderStatus) -> 'Order':
        """Update the order status."""
        self.status = new_status
        db.add(self)
        db.commit()
        db.refresh(self)
        return self
    
    def calculate_totals(self) -> None:
        """Calculate order totals based on order items."""
        self.subtotal = sum(item.price * item.quantity for item in self.items)
        # Simple tax calculation (example: 10% tax)
        self.tax_amount = self.subtotal * 0.1
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost
    
    @classmethod
    def get_customer_orders(cls, db, customer_id: int, skip: int = 0, limit: int = 100):
        """Get all orders for a specific customer."""
        return (
            db.query(cls)
            .filter(cls.customer_id == customer_id)
            .order_by(cls.order_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

class OrderItem(Base):
    """Individual items within an order."""
    
    __tablename__ = "order_items"
    
    order_id = Column(ForeignKey('orders.id'), nullable=False)
    product_id = Column(ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # Price at time of purchase
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('price >= 0', name='check_price_non_negative'),
    )
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} @ ${self.price:.2f}"
    
    @property
    def total_price(self) -> float:
        """Calculate the total price for this line item."""
        return float(self.price * self.quantity)

# Add Order and OrderItem to the Base's registry
Base.metadata.tables['orders'] = Order.__table__
Base.metadata.tables['order_items'] = OrderItem.__table__
