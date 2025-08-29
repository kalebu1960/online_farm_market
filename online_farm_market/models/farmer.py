"""Farmer model for farm management."""
from typing import List, Optional

from sqlalchemy import Column, String, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship, Session

from ..db import Base
from .base import BaseModel

class Farmer(Base, BaseModel):
    """Farmer model representing farm owners and their information."""
    __tablename__ = "farmers"
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    farm_name = Column(String(100), nullable=False)
    bio = Column(Text)
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    
    # Relationships
    user = relationship("User", back_populates="farmer_profile")
    products = relationship("Product", back_populates="farmer", cascade="all, delete-orphan")
    
    @classmethod
    def get_by_user_id(cls, db: Session, user_id: int) -> Optional['Farmer']:
        """Get a farmer by their user ID."""
        return db.query(cls).filter(cls.user_id == user_id).first()
    
    @classmethod
    def create(
        cls, 
        db: Session, 
        user_id: int,
        farm_name: str,
        **kwargs
    ) -> 'Farmer':
        """Create a new farmer profile."""
        return super().create(
            db,
            user_id=user_id,
            farm_name=farm_name,
            **kwargs
        )
    
    def to_dict(self) -> dict:
        """Convert farmer to dictionary."""
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'farm_name': self.farm_name,
            'bio': self.bio,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
        })
        
        # Include user information if available
        if self.user:
            data['user'] = self.user.to_dict()
            
        return data
