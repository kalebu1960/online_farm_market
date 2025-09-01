from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__)
products_bp = Blueprint('products', __name__)
transactions_bp = Blueprint('transactions', __name__)

# Import routes after creating blueprints to avoid circular imports
from . import auth, products, transactions
