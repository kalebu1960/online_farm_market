"""
Main CLI module for the Online Farm Market application.
"""
import os
import sys
import click
from typing import Optional
from rich.console import Console
from rich.theme import Theme

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import local modules
from . import auth, products, transactions
from ..db import get_db, init_db

# Initialize console with custom theme
custom_theme = Theme({
    "success": "green",
    "error": "bold red",
    "warning": "yellow",
    "info": "cyan",
    "title": "bold blue",
    "highlight": "magenta"
})
console = Console(theme=custom_theme)

db = next(get_db())

@click.group()
@click.version_option(version="1.0.0", message="%(version)s")
@click.pass_context
def cli(ctx):
    """Online Farm Market - A CLI application for managing farm products and transactions."""
    # Ensure the database is initialized
    init_db()
    ctx.ensure_object(dict)
    ctx.obj['db'] = db
    ctx.obj['console'] = console

def main():
    """Entry point for the CLI application."""
    # Check if the database exists, if not, create it
    if not os.path.exists("farm_market.db"):
        console.print("Initializing database...", style="info")
        init_db()
        console.print("Database initialized successfully!", style="success")
    
    # Run the CLI
    cli(obj={})

# Add command groups
cli.add_command(auth.auth_group)
cli.add_command(products.products_group)

if __name__ == "__main__":
    main()
