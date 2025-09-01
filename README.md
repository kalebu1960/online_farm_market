# Online Farm Market

An online marketplace for local farmers to sell their produce directly to consumers.

## Features

- User authentication (Farmers and Customers)
- Product listings with categories
- Shopping cart functionality
- Order management
- Farmer dashboard
- Customer profiles

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- SQLite (for development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/online_farm_market.git
   cd online_farm_market
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .[dev]
   ```

4. Set up the database:
   ```bash
   alembic upgrade head
   ```

5. Run the development server:
   ```bash
   uvicorn online_farm_market.main:app --reload
   ```

## Project Structure

```
online_farm_market/
├── alembic/               # Database migrations
├── online_farm_market/    # Main package
│   ├── cli/              # Command-line interface
│   ├── models/           # Database models
│   ├── routes/           # API routes
│   ├── static/           # Static files (CSS, JS, images)
│   └── templates/        # HTML templates
├── tests/                # Test files
├── .env                  # Environment variables
├── .gitignore
├── alembic.ini           # Alembic configuration
├── pyproject.toml        # Project metadata and dependencies
└── README.md
```

## Development

### Running Tests

```bash
pytest
```

### Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Run the following commands before committing:

```bash
black .
isort .
flake8
mypy .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
