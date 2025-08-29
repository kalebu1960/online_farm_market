from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Numeric, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum
from typing import List, Optional, Type, TypeVar

# Type variable for generic class methods
T = TypeVar('T', bound='BaseModel')

# Database configuration
DATABASE_URL = "sqlite:///farm_market.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    FARMER = "farmer"
    ADMIN = "admin"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Models
class BaseModel:
    """Base model with common functionality for all models"""
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @classmethod
    def get_all(cls, db, skip: int = 0, limit: int = 100) -> List[Type['T']]:
        return db.query(cls).offset(skip).limit(limit).all()
    
    @classmethod
    def get_by_id(cls, db, id: int) -> Optional[Type['T']]:
        return db.query(cls).filter(cls.id == id).first()
    
    @classmethod
    def create(cls, db, **kwargs) -> Type['T']:
        obj = cls(**kwargs)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    
    def update(self, db, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.commit()
        db.refresh(self)
    
    def delete(self, db) -> None:
        db.delete(self)
        db.commit()

class User(Base, BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20))
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    farmer_profile = relationship("Farmer", back_populates="user", uselist=False)
    customer_profile = relationship("Customer", back_populates="user", uselist=False)
    transactions = relationship("Transaction", back_populates="user")
    
    @classmethod
    def get_by_email(cls, db, email: str) -> Optional['User']:
        return db.query(cls).filter(cls.email == email).first()

class Farmer(Base, BaseModel):
    __tablename__ = "farmers"
    
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    farm_name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    address = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zip_code = Column(String(20), nullable=False)
    phone_number = Column(String(20), nullable=False)
    whatsapp_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="farmer_profile")
    products = relationship("Product", back_populates="farmer")
    
    @classmethod
    def get_by_user_id(cls, db, user_id: int) -> Optional['Farmer']:
        return db.query(cls).filter(cls.user_id == user_id).first()

class Product(Base, BaseModel):
    __tablename__ = "products"
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(String(50), nullable=False, default="1")
    unit = Column(String(20), nullable=True)
    category = Column(String(50), nullable=False)
    condition = Column(String(20), nullable=False, default="new")
    status = Column(String(20), nullable=False, default="available")
    location = Column(String(100), nullable=False)
    is_negotiable = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    views = Column(Integer, default=0)
    farmer_id = Column(Integer, ForeignKey('farmers.id'), nullable=False)
    
    # Image handling (in a real app, this would be a separate table)
    image_urls = Column(Text, nullable=True)
    
    # Relationships
    farmer = relationship("Farmer", back_populates="products")
    
    def increment_views(self, db):
        """Increment the view count for this product."""
        self.views = (self.views or 0) + 1
        db.commit()
    
    def mark_as_sold(self, db):
        """Mark the product as sold."""
        self.status = "sold"
        db.commit()
    
    def get_image_urls(self):
        """Return a list of image URLs."""
        if not self.image_urls:
            return []
        return self.image_urls.split(',')
    
    @classmethod
    def get_by_farmer_id(cls, db, farmer_id: int, skip: int = 0, limit: int = 100) -> List['Product']:
        return db.query(cls).filter(cls.farmer_id == farmer_id).offset(skip).limit(limit).all()
    def get_available_products(cls, db, skip: int = 0, limit: int = 100) -> List['Product']:
        return db.query(cls).filter(cls.quantity_available > 0).offset(skip).limit(limit).all()

class Customer(Base, BaseModel):
    __tablename__ = "customers"
    
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    shipping_address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    
    # Relationships
    user = relationship("User", back_populates="customer_profile")
    transactions = relationship("Transaction", back_populates="customer")
    
    @classmethod
    def get_by_user_id(cls, db, user_id: int) -> Optional['Customer']:
        return db.query(cls).filter(cls.user_id == user_id).first()

class Transaction(Base, BaseModel):
    __tablename__ = "transactions"
    
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    shipping_address = Column(String(255))
    payment_method = Column(String(50))
    payment_status = Column(String(50))
    
    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
    items = relationship("TransactionItem", back_populates="transaction")
    
    @classmethod
    def get_by_customer_id(cls, db, customer_id: int, skip: int = 0, limit: int = 100) -> List['Transaction']:
        return db.query(cls).filter(cls.customer_id == customer_id).order_by(cls.created_at.desc()).offset(skip).limit(limit).all()

class TransactionItem(Base, BaseModel):
    __tablename__ = "transaction_items"
    
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price_per_unit = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product", back_populates="transaction_items")

def get_db():
    """Provides a new database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Creates all database tables."""
    Base.metadata.create_all(bind=engine)
