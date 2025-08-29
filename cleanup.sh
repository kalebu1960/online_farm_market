#!/bin/bash

# Remove Python cache directories
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type d -name "*.pyc" -delete
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type d -name "*.egg-info" -exec rm -r {} +

# Remove test database and cache
rm -f test_farm_market.db
rm -f .pytest_cache/

# Remove old database files (keep a backup just in case)
if [ -f "farm_market.db" ]; then
    cp farm_market.db farm_market.db.backup
    echo "Created backup at farm_market.db.backup"
fi

# Remove duplicate directories
rm -rf farm_market_cli/
rm -rf online_farmarket/

# Remove any .DS_Store files (Mac)
find . -name ".DS_Store" -delete

echo "Cleanup complete!"
