"""Customer model for marketplace users."""
from typing import List, Optional

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, Session

from ..db import Base
from .base import BaseModel

class Customer(Base, BaseModel):
    """Customer model representing marketplace buyers."""
    __tablename__ = "customers"
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    shipping_address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    
    # Relationships
    user = relationship("User", back_populates="customer_profile")
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
    
    @classmethod
    def get_by_user_id(cls, db: Session, user_id: int) -> Optional['Customer']:
        """Get a customer by their user ID."""
        return db.query(cls).filter(cls.user_id == user_id).first()
    
    @classmethod
    def create(
        cls, 
        db: Session, 
        user_id: int,
        **kwargs
    ) -> 'Customer':
        """Create a new customer profile."""
        return super().create(
            db,
            user_id=user_id,
            **kwargs
        )
    
    def to_dict(self) -> dict:
        """Convert customer to dictionary."""
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'shipping_address': self.shipping_address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
        })
        
        # Include user information if available
        if self.user:
            data['user'] = self.user.to_dict()
            
        return data
