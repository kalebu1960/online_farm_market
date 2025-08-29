"""
Tests for authentication functionality.
"""
import pytest
from click.testing import CliRunner
from rich.console import Console
from sqlalchemy.orm import Session

from online_farm_market.cli.auth import auth_group
from online_farm_market.models.user import User, UserRole
from online_farm_market.models.customer import Customer
from online_farm_market.db import get_db, init_db

# Initialize test database
@pytest.fixture(scope='module')
def test_db():
    # Set up in-memory SQLite database for testing
    db = next(get_db())
    init_db()
    try:
        yield db
    finally:
        db.close()

# Create a test app
@pytest.fixture
def runner():
    return CliRunner()

def test_simple_login(runner, test_db):
    """Test login with a simple user creation."""
    # Test credentials
    test_email = "simple_test@example.com"
    test_password = "SimplePass123!"
    
    # Create a new session for this test
    db = test_db
    
    try:
        # Clean up any existing test user
        existing_user = db.query(User).filter_by(email=test_email).first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
        
        # Create a test user directly
        user = User(
            email=test_email,
            hashed_password=User.hash_password(test_password),
            full_name="Test User",
            phone_number="+1234567890",
            role=UserRole.CUSTOMER,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create customer profile
        customer = Customer(user_id=user.id)
        db.add(customer)
        db.commit()
        
        # Verify user was created
        db_user = db.query(User).filter_by(email=test_email).first()
        assert db_user is not None, "User was not created in the database"
        
        # Debug: Print user details
        print("\n=== Test User Details ===")
        print(f"User ID: {db_user.id}")
        print(f"Email: {db_user.email}")
        print(f"Hashed Password: {db_user.hashed_password}")
        print(f"Is Active: {db_user.is_active}")
        print(f"Password Verified: {db_user.verify_password(test_password)}")
        
        # Create a console instance for testing
        console = Console()
        
        # Test login using the auth_group directly
        result = runner.invoke(
            auth_group,
            ["login"],
            input=f"{test_email}\n{test_password}\n",
            obj={'db': db, 'console': console}
        )
        
        # Debug output
        print("\n=== Login Test Output ===")
        print(f"Exit code: {result.exit_code}")
        print(f"Output: {result.output}")
        print("======================\n")
        
        # Basic assertions
        assert result.exit_code == 0, f"Login failed with exit code {result.exit_code}"
        assert any(term in result.output.lower() for term in ["login successful", "welcome"]), \
            f"Expected login success message, got: {result.output}"
        
    except Exception as e:
        print(f"\n=== Test Error ===")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        db.rollback()
        raise
    finally:
        # Cleanup
        db.rollback()
        user = db.query(User).filter_by(email=test_email).first()
        if user:
            # Delete customer first due to foreign key constraint
            customer = db.query(Customer).filter_by(user_id=user.id).first()
            if customer:
                db.delete(customer)
            db.delete(user)
            db.commit()
