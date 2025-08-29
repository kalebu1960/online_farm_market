"""
Pytest configuration and fixtures for testing the Online Farm Market application.
"""
import os
import sys
import pytest
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import sessionmaker, Session

# Set testing environment variable
os.environ["TESTING"] = "true"

# Import the main app components
from online_farm_market.cli.main import cli
from online_farm_market.db import Base, get_db

# Import all models to ensure they are registered with SQLAlchemy
from online_farm_market.models.user import User, UserRole
from online_farm_market.models.farmer import Farmer
from online_farm_market.models.product import Product
from online_farm_market.models.customer import Customer
from online_farm_market.models.transaction import Transaction, TransactionStatus, TransactionItem

# Test database URL - using in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine."""
    # Create engine with SQLite in-memory database for testing
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True  # Enable SQL logging for debugging
    )
    
    # Drop all existing tables
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables with the current schema
    Base.metadata.create_all(bind=engine)
    
    # Verify tables were created
    inspector = inspect(engine)
    print("\nTables in test database:")
    for table_name in inspector.get_table_names():
        print(f"- {table_name}")
        
        # Print columns for debugging
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        print(f"  Columns: {', '.join(columns)}")
    
    yield engine
    
    # Clean up
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture
def db_session(engine):
    """
    Create a new database session for a test.
    Each test gets its own database transaction that is rolled back after the test.
    """
    # Create a new connection and transaction
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create a session
    Session = sessionmaker(bind=connection, expire_on_commit=False)
    session = Session()
    
    # Begin a nested transaction
    session.begin_nested()
    
    # Set up savepoint for rollback after each test
    @event.listens_for(session, 'after_transaction_end')
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            session.begin_nested()
    
    # Store the original get_db function
    from online_farm_market.db import get_db as original_get_db
    
    # Override get_db to return our test session
    def get_test_db():
        try:
            yield session
        finally:
            pass  # Don't close the session here, we'll handle it in the fixture
    
    # Monkey patch get_db for the test
    import online_farm_market.db
    online_farm_market.db.get_db = get_test_db
    
    try:
        yield session
    finally:
        # Clean up after test
        session.close()
        transaction.rollback()
        connection.close()
        
        # Restore original get_db
        online_farm_market.db.get_db = original_get_db

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    # Delete any existing test user first to avoid unique constraint violations
    existing_user = db_session.query(User).filter_by(email="test@example.com").first()
    if existing_user:
        db_session.delete(existing_user)
        db_session.commit()
    
    # Create a new test user
    user = User(
        email="test@example.com",
        hashed_password=User.hash_password("testpassword"),
        full_name="Test User",
        phone_number="+1234567890",
        role=UserRole.CUSTOMER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_farmer(db_session, test_user):
    """Create a test farmer."""
    farmer = Farmer(
        user_id=test_user.id,
        farm_name="Test Farm",
        bio="Test Bio",
        address="123 Test St",
        city="Testville",
        state="TS",
        zip_code="12345"
    )
    db_session.add(farmer)
    db_session.commit()
    db_session.refresh(farmer)
    return farmer

@pytest.fixture
def test_product(db_session, test_farmer):
    """Create a test product."""
    product = Product(
        name="Test Product",
        description="Test Description",
        price=9.99,
        quantity_available=100,
        unit="kg",
        category="vegetables",
        is_organic=True,
        farmer_id=test_farmer.id
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product

@pytest.fixture
def test_customer(db_session, test_user):
    """Create a test customer."""
    customer = Customer(
        user_id=test_user.id,
        shipping_address="123 Customer St",
        city="Customerville",
        state="CS",
        zip_code="54321"
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer

@pytest.fixture
def test_transaction(db_session, test_customer, test_product):
    """Create a test transaction."""
    from datetime import datetime
    from online_farm_market.models.transaction import TransactionStatus
    
    # Create the transaction
    transaction = Transaction(
        customer_id=test_customer.id,
        user_id=test_customer.user_id,
        total_amount=19.98,
        status=TransactionStatus.PENDING,
        payment_method="credit_card",
        payment_status="pending",
        shipping_address=test_customer.shipping_address,
        city=test_customer.city,
        state=test_customer.state,
        zip_code=test_customer.zip_code,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    
    # Create transaction item
    item = TransactionItem(
        transaction_id=transaction.id,
        product_id=test_product.id,
        quantity=2,
        unit_price=9.99,
        total_price=19.98
    )
    
    db_session.add(item)
    db_session.commit()
    db_session.refresh(transaction)
    
    # Add items to the transaction
    transaction.items = [item]
    db_session.commit()
    
    return transaction
