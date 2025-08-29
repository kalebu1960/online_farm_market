"""User model for authentication and authorization."""
import enum
import hashlib
import secrets
from typing import Optional

from sqlalchemy import Column, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship, Session

from ..db import Base
from .base import BaseModel

class UserRole(str, enum.Enum):
    """User roles for authorization."""
    CUSTOMER = "customer"
    FARMER = "farmer"
    ADMIN = "admin"

class User(Base, BaseModel):
    """User model for authentication and basic user information."""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20))
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    farmer_profile = relationship("Farmer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    customer_profile = relationship("Customer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user")
    
    @classmethod
    def get_by_email(cls, db: Session, email: str) -> Optional['User']:
        """Get a user by their email address."""
        return db.query(cls).filter(cls.email == email).first()
    
    @classmethod
    def create(
        cls, 
        db: Session, 
        email: str, 
        password: str, 
        full_name: str,
        role: UserRole = UserRole.CUSTOMER,
        **kwargs
    ) -> 'User':
        """Create a new user with a hashed password."""
        hashed_password = cls.hash_password(password)
        return super().create(
            db,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            **kwargs
        )
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storing."""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000,
            dklen=128
        ).hex()
        return f"{salt}${pwd_hash}"
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        if not self.hashed_password or '$' not in self.hashed_password:
            return False
        
        salt, stored_hash = self.hashed_password.split('$', 1)
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000,
            dklen=128
        ).hex()
        
        return secrets.compare_digest(new_hash, stored_hash)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary, excluding sensitive data."""
        data = super().to_dict()
        data.update({
            'email': self.email,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'role': self.role.value,
            'is_active': self.is_active,
        })
        # Remove hashed password from the output
        if 'hashed_password' in data:
            del data['hashed_password']
        return data
