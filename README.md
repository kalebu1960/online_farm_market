 Online Farm Market

A full-featured online marketplace connecting local farmers directly with consumers, built with Python, FastAPI, and SQLAlchemy.

## 🌟 Features

### For Customers
- Browse and search farm-fresh products
- Secure user authentication and profile management
- Shopping cart and wishlist functionality
- Order tracking and history
- Secure payment processing

### For Farmers
- Farmer dashboard with sales analytics
- Product and inventory management
- Order fulfillment tools
- Customer communication
- Sales reports and insights

### Technical Features
- RESTful API architecture
- JWT Authentication
- Database migrations with Alembic
- Comprehensive test coverage
- CI/CD ready

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- SQLite (development) / PostgreSQL (production)

### Installation

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/kalebu1960/online_farm_market.git](https://github.com/kalebu1960/online_farm_market.git)
   cd online_farm_market
undefined
Set up a virtual environment:
bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
Install dependencies:
bash
pip install -e ".[dev]"  # For development with testing packages
Set up environment variables:
bash
cp .env.example .env
# Edit .env with your configuration
Initialize the database:
bash
alembic upgrade head
python scripts/seed_database.py  # Optional: Load sample data
Run the development server:
bash
uvicorn online_farm_market.main:app --reload
🏗️ Project Structure
online_farm_market/
├── alembic/                 # Database migrations
│   └── versions/           # Migration files
│
├── docs/                    # Documentation
│   ├── api/                # API documentation
│   ├── architecture/       # System architecture
│   └── setup/              # Setup guides
│
├── online_farm_market/      # Main package
│   ├── api/                # API endpoints
│   │   └── v1/            # API version 1
│   │
│   ├── cli/                # Command-line interface
│   │   ├── commands/      # CLI commands
│   │   └── __init__.py
│   │
│   ├── core/               # Core functionality
│   │   ├── config.py      # Configuration
│   │   ├── database.py    # Database setup
│   │   └── security.py    # Authentication
│   │
│   ├── models/            # Database models
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── farmer.py
│   │   └── transaction.py
│   │
│   ├── services/          # Business logic
│   │   ├── auth.py
│   │   ├── payment.py
│   │   └── products.py
│   │
│   └── utils/             # Utility functions
│       └── helpers.py
│
├── scripts/               # Utility scripts
│   ├── setup_db.py
│   └── populate_data.py
│
├── static/                # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── conftest.py       # Test configuration
│
├── .env.example          # Example environment variables
├── .gitignore
├── alembic.ini           # Alembic configuration
├── pyproject.toml        # Project metadata
└── README.md
🧪 Testing
Run the test suite:

bash
pytest
Code Quality
This project enforces code quality with:

Black for code formatting
isort for import sorting
flake8 for linting
mypy for type checking
Run all checks:

bash
black .
isort .
flake8
mypy .
🤝 Contributing
Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.


Caleb Muindi

Project Link: https://github.com/kalebu1960/online_farm_market