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
    assert "auth" in result.output
    assert "products" in result.output
    assert "orders" in result.output

def test_register_new_user(runner, db_session):
    """Test registering a new user through the CLI."""
    # Test data
    test_email = "test_register_new@example.com"
    test_password = "testpass123"
    
    # Delete user if it already exists
    existing_user = db_session.query(User).filter(User.email == test_email).first()
    if existing_user:
        db_session.delete(existing_user)
        db_session.commit()
    
    # Run the register command with the test runner
    result = runner.invoke(
        cli,
        [
            "auth", "register",
            "--email", test_email,
            "--password", test_password,
            "--full-name", "Test User",
            "--phone", "+1234567890",
            "--role", "customer"
        ],
        input=f"{test_password}\n",  # Confirm password
        obj={'db': db_session, 'console': Console()}
    )
    
    # Check that the command executed successfully
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    
    # Check that the user was created in the database
    user = db_session.query(User).filter(User.email == test_email).first()
    assert user is not None, "User was not created in the database"
    assert user.full_name == "Test User"
    assert user.phone_number == "+1234567890"
    assert user.role == UserRole.CUSTOMER  # Check enum value
    
    # Check for success message in the output
    output = result.output.lower()
    assert any(term in output for term in ["success", "created", "welcome"]), \
        f"Expected success message, got: {result.output}"

def test_login_success(runner, db_session, test_user):
    """Test successful user login."""
    # Set the test user's password
    test_user.hashed_password = User.hash_password("testpassword")
    db_session.add(test_user)
    db_session.commit()

    # Run the login command
    result = runner.invoke(
        cli,
        ["auth", "login"],
        input="test@example.com\ntestpassword\n",
        obj={'db': db_session, 'console': Console()}
    )

    # Check for successful login message
    output = result.output.lower()
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    assert 'login successful' in output or 'welcome' in output, \
        f"Expected success message, got: {output}"

def test_list_products(runner, db_session, test_product):
    """Test listing products through the CLI."""
    # Ensure the test product is in the database
    db_session.add(test_product)
    db_session.commit()
    
    # Run the products list command
    result = runner.invoke(
        cli, 
        ["products"],  # List products using the default command
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
    
    # Run the view order command with the order ID as a positional argument
    result = runner.invoke(
        cli,
        ["transactions", "view", str(test_transaction.id)],
        obj={
            'db': db_session, 
            'console': Console(),
            'user_id': test_user.id  # Simulate authenticated user
        }
    )
    
    # Check that the command executed successfully
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    
    # Check that the transaction ID is in the output
    output = result.output.lower()
    assert str(test_transaction.id) in output, \
        f"Transaction ID {test_transaction.id} not found in output: {result.output}"
        ["transactions", "view", str(test_transaction.id)],
        obj={
            'db': db_session,
            'console': Console(),
            'user_id': test_user.id  # Simulate authenticated user
        }
    )
    
    # Check that the command executed successfully
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    
    # Check for expected output
    output = result.output.lower()
    assert str(test_transaction.id) in output, f"Order ID not found in output: {result.output}"
