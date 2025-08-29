"""Product model for farm products."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey, Boolean, DateTime, event
from sqlalchemy.orm import relationship, Session

from ..db import Base
from .base import BaseModel

class Product(Base, BaseModel):
    """Product model representing farm products for sale in the marketplace."""
    __tablename__ = "products"
    
    # Basic information
    title = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(String(50), nullable=False)  # e.g., "5 kg", "10 pieces"
    unit = Column(String(20))  # kg, g, lb, each, etc.
    category = Column(String(50), nullable=False)  # vegetable, fruit, dairy, etc.
    condition = Column(String(20), default='new')  # new, used, refurbished
    status = Column(String(20), default='available')  # available, sold, reserved
    location = Column(String(100), nullable=False)  # City/area where product is located
    is_negotiable = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    views = Column(Integer, default=0)
    image_urls = Column(Text)  # Comma-separated URLs of product images
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Foreign keys
    farmer_id = Column(Integer, ForeignKey('farmers.id', ondelete='CASCADE'), nullable=False)
    
    # Relationships
    farmer = relationship("Farmer", back_populates="products")
    transaction_items = relationship("TransactionItem", back_populates="product")
    
    # For backward compatibility
    @property
    def name(self):
        return self.title
        
    @property
    def quantity_available(self):
        try:
            return int(self.quantity.split()[0])
        except (ValueError, AttributeError):
            return 0
            
    @property
    def is_organic(self):
        return 'organic' in self.title.lower() or 'organic' in self.description.lower()
    
    def increment_views(self, db: Session):
        """Increment the view count for this product."""
        self.views += 1
        db.commit()
        
    def mark_as_sold(self, db: Session):
        """Mark this product as sold."""
        self.status = 'sold'
        db.commit()
        
    def get_image_urls(self) -> List[str]:
        """Get a list of image URLs."""
        if not self.image_urls:
            return []
        return [url.strip() for url in self.image_urls.split(',') if url.strip()]
    
    @classmethod
    def get_by_farmer_id(
        cls, 
        db: Session, 
        farmer_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List['Product']:
        """Get all products for a specific farmer."""
        return (
            db.query(cls)
            .filter(cls.farmer_id == farmer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    @classmethod
    def get_available_products(
        cls, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List['Product']:
        """Get all products that are in stock."""
        return (
            db.query(cls)
            .filter(cls.quantity_available > 0)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    @classmethod
    def search(
        cls,
        db: Session,
        query: str = None,
        category: str = None,
        min_price: float = None,
        max_price: float = None,
        organic_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List['Product']:
        """Search products with filters."""
        query_builder = db.query(cls)
        
        if query:
            query_builder = query_builder.filter(
                (cls.name.ilike(f"%{query}%")) | 
                (cls.description.ilike(f"%{query}%"))
            )
            
        if category:
            query_builder = query_builder.filter(cls.category.ilike(f"%{category}%"))
            
        if min_price is not None:
            query_builder = query_builder.filter(cls.price >= Decimal(str(min_price)))
            
        if max_price is not None:
            query_builder = query_builder.filter(cls.price <= Decimal(str(max_price)))
            
        if organic_only:
            query_builder = query_builder.filter(cls.is_organic == True)
            
        return query_builder.offset(skip).limit(limit).all()
    
    def to_dict(self) -> dict:
        """Convert product to dictionary."""
        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price is not None else None,
            'quantity_available': self.quantity_available,
            'unit': self.unit,
            'category': self.category,
            'is_organic': self.is_organic,
            'farmer_id': self.farmer_id,
        })
        
        # Include farmer information if available
        if self.farmer:
            data['farmer'] = {
                'id': self.farmer.id,
                'farm_name': self.farmer.farm_name,
                'city': self.farmer.city,
                'state': self.farmer.state,
            }
            
        return data
