"""Base model with common functionality for all models."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, DateTime, func

# Type variable for generic class methods
T = TypeVar('T', bound='BaseModel')

class BaseModel:
    """Base model with common functionality for all models."""
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @classmethod
    def get_all(cls, db: Session, skip: int = 0, limit: int = 100) -> List[Type['T']]:
        """Get all instances of the model with pagination."""
        return db.query(cls).offset(skip).limit(limit).all()
    
    @classmethod
    def get_by_id(cls, db: Session, id: int) -> Optional[Type['T']]:
        """Get a single instance by its ID."""
        return db.query(cls).filter(cls.id == id).first()
    
    @classmethod
    def create(cls, db: Session, **kwargs) -> Type['T']:
        """Create a new instance with the given attributes."""
        obj = cls(**kwargs)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    
    def update(self, db: Session, **kwargs) -> None:
        """Update the instance with the given attributes."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(self)
    
    def delete(self, db: Session) -> None:
        """Delete the instance from the database."""
        db.delete(self)
        db.commit()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model instance to a dictionary."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
