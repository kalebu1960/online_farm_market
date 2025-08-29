"""
Tests for the Online Farm Market CLI commands.
"""
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from rich.console import Console

# Import the main CLI app
from online_farm_market.cli.main import cli
from online_farm_market.models.user import User, UserRole

@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()

def test_cli_help(runner):
    """Test that the CLI shows help information."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Online Farm Market" in result.output
    assert "auth-group" in result.output
    assert "products-group" in result.output
    assert "transactions" in result.output

def test_register_new_user(runner, db_session):
    """Test registering a new user through the CLI."""
    import uuid
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError
    
    # Generate a unique email for this test
    test_email = f"test_register_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "Testpass123!"  # Meets password requirements
    
    # Create a new session for the test to avoid transaction conflicts
    from sqlalchemy.orm import sessionmaker
    from online_farm_market.db import engine
    
    # Create a new session factory
    Session = sessionmaker(bind=engine)
    test_db = Session()
    
    try:
        # Clean up any existing user with the same email
        existing_user = test_db.query(User).filter(User.email == test_email).first()
        if existing_user:
            # Delete related records first due to foreign key constraints
            test_db.execute(text('DELETE FROM customers WHERE user_id = :user_id'), 
                          {'user_id': existing_user.id})
            test_db.execute(text('DELETE FROM farmers WHERE user_id = :user_id'), 
                          {'user_id': existing_user.id})
            test_db.delete(existing_user)
            test_db.commit()
        
        # Run the register command with the test runner
        result = runner.invoke(
            cli,
            ["auth-group", "register"],
            input=f"{test_email}\n{test_password}\n{test_password}\nTest User\n+1234567890\ncustomer\n",
            obj={'db': test_db, 'console': Console()}
        )
        
        # Debug output
        print("\n=== Register Command Output ===")
        print(result.output)
        print("============================\n")
        
        # Check that the command executed successfully
        assert result.exit_code == 0, f"Command failed with output: {result.output}"
        
        # Commit any pending changes
        test_db.commit()
        
        # Check that the user was created in the database
        user = test_db.query(User).filter(User.email == test_email).first()
        assert user is not None, f"User was not created in the database. Output: {result.output}"
        
        # Verify user data
        assert user.email == test_email
        assert user.full_name == "Test User"
        assert user.phone_number == "+1234567890"
        assert user.role == UserRole.CUSTOMER
        assert user.is_active is True
        
        # Verify password was hashed
        assert user.hashed_password != test_password
        assert user.verify_password(test_password)
        
        # Check for success message in the output
        output = result.output.lower()
        assert any(term in output for term in ["success", "created", "welcome"]), \
            f"Expected success message, got: {result.output}"
            
    except Exception as e:
        test_db.rollback()
        raise e
    finally:
        # Clean up after test
        try:
            # Find and delete the test user if it exists
            user = test_db.query(User).filter(User.email == test_email).first()
            if user:
                # Delete related customer record first due to foreign key constraint
                test_db.execute(text('DELETE FROM customers WHERE user_id = :user_id'), 
                              {'user_id': user.id})
                test_db.delete(user)
                test_db.commit()
        except Exception as e:
            test_db.rollback()
            print(f"Error during test cleanup: {e}")
        finally:
            test_db.close()

def test_login_success(runner, db_session):
    """Test successful user login."""
    from online_farm_market.models.user import User, UserRole
    from online_farm_market.models.customer import Customer
    
    # Create a fresh test user directly in the test
    test_email = "test_login@example.com"
    test_password = "TestPass123!"
    
    # Clean up any existing test user
    existing_user = db_session.query(User).filter_by(email=test_email).first()
    if existing_user:
        db_session.delete(existing_user)
        db_session.commit()
    
    try:
        # Create a new test user with a known password
        user = User(
            email=test_email,
            hashed_password=User.hash_password(test_password),
            full_name="Test User",
            phone_number="+1234567890",
            role=UserRole.CUSTOMER,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create customer profile
        customer = Customer(user_id=user.id)
        db_session.add(customer)
        db_session.commit()
        
        # Run the login command with the test runner
        result = runner.invoke(
            cli,
            ["auth-group", "login"],
            input=f"{test_email}\n{test_password}\n",
            obj={'db': db_session, 'console': Console()}
        )
        
        # Debug output
        print("\n=== Login Command Output ===")
        print(result.output)
        print("==========================\n")
        
        # Check that the command executed successfully
        assert result.exit_code == 0, f"Login failed with output: {result.output}"
        
        # Check for success message in the output
        output = result.output.lower()
        success_terms = ["login successful", "welcome", "welcome back"]
        assert any(term in output for term in success_terms), \
            f"Expected login success message, got: {result.output}"
    
    finally:
        # Clean up
        db_session.rollback()
        user = db_session.query(User).filter_by(email=test_email).first()
        if user:
            db_session.delete(user)
            db_session.commit()

def test_list_products(runner, db_session, test_product):
    """Test listing products through the CLI."""
    # Ensure the test product is in the database
    db_session.add(test_product)
    db_session.commit()
    
    # Run the products list command
    result = runner.invoke(
        cli, 
        ["products-group", "list"],  # List products using the products-group list command
        obj={'db': db_session, 'console': Console()}
    )
    
    # Check that the command executed successfully
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    
    # Check that the product is listed in the output
    output = result.output.lower()
    assert test_product.name.lower() in output, \
        f"Product name '{test_product.name}' not found in output: {result.output}"

def test_view_order(runner, db_session, test_transaction, test_user):
    """Test viewing an order through the CLI."""
    # Add the test transaction to the database
    db_session.add(test_transaction)
    db_session.commit()
    
    # Run the view order command
    result = runner.invoke(
        cli,
        ["transactions", "view", str(test_transaction.id)],
        obj={'db': db_session, 'console': Console(), 'user': test_user}
    )
    
    # Check that the command executed successfully
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    
    # Check that the transaction ID is in the output
    output = result.output.lower()
    assert str(test_transaction.id) in output, \
        f"Transaction ID {test_transaction.id} not found in output: {result.output}"
    
    # Check for expected output
    output = result.output.lower()
    assert str(test_transaction.id) in output, f"Order ID not found in output: {result.output}"
