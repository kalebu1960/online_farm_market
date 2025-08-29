""
Utility functions for the Online Farm Market CLI.
"""
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.text import Text
from sqlalchemy.orm import Session

T = TypeVar('T')

def confirm_action(prompt: str, default: bool = False) -> bool:
    """Prompt the user to confirm an action."""
    try:
        return input(f"{prompt} [{'Y/n' if default else 'y/N'}] ").strip().lower() \
            in (['y', 'yes'] + ([''] if default else []))
    except (KeyboardInterrupt, EOFError):
        return False

def format_currency(amount: float) -> str:
    """Format a number as currency."""
    return f"${amount:,.2f}"

def format_date(date: datetime) -> str:
    """Format a datetime as a human-readable date."""
    return date.strftime("%b %d, %Y")

def format_datetime(dt: datetime) -> str:
    """Format a datetime as a human-readable string."""
    return dt.strftime("%b %d, %Y %I:%M %p")

def display_table(
    data: List[Dict[str, Any]],
    columns: Dict[str, str],
    title: Optional[str] = None
) -> None:
    """
    Display tabular data in a formatted table.
    
    Args:
        data: List of dictionaries where each dictionary represents a row
        columns: Dictionary mapping field names to column headers
        title: Optional title for the table
    """
    if not data:
        console = Console()
        console.print("\n[info]No data to display.[/]")
        return
    
    table = Table(title=f"\n{title}" if title else None, show_header=True, header_style="bold magenta")
    
    # Add columns
    for field, header in columns.items():
        table.add_column(header)
    
    # Add rows
    for row in data:
        table.add_row(*[str(row.get(field, "")) for field in columns.keys()])
    
    console = Console()
    console.print(table)

def paginate_items(
    items: List[T],
    page: int = 1,
    per_page: int = 10,
    formatter: callable = None
) -> Dict[str, Any]:
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Current page number (1-based)
        per_page: Number of items per page
        formatter: Optional function to format each item
    
    Returns:
        Dictionary containing paginated items and metadata
    """
    if not items:
        return {
            'items': [],
            'page': 1,
            'per_page': per_page,
            'total': 0,
            'total_pages': 0,
            'has_prev': False,
            'has_next': False
        }
    
    total = len(items)
    total_pages = (total + per_page - 1) // per_page
    page = max(1, min(page, total_pages))
    
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_items = items[start:end]
    
    if formatter:
        paginated_items = [formatter(item) for item in paginated_items]
    
    return {
        'items': paginated_items,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': end < total
    }

def display_paginated(
    items: List[Dict[str, Any]],
    columns: Dict[str, str],
    title: str = "Results",
    page: int = 1,
    per_page: int = 10
) -> None:
    """
    Display paginated data in a table with navigation controls.
    
    Args:
        items: List of dictionaries where each dictionary represents a row
        columns: Dictionary mapping field names to column headers
        title: Title for the table
        page: Current page number (1-based)
        per_page: Number of items per page
    """
    if not items:
        console = Console()
        console.print("\n[info]No data to display.[/]")
        return
    
    paginated = paginate_items(items, page, per_page)
    
    # Display the current page
    display_table(
        data=paginated['items'],
        columns=columns,
        title=f"{title} (Page {paginated['page']} of {paginated['total_pages'] or 1})"
    )
    
    # Display pagination controls
    console = Console()
    pagination = []
    
    if paginated['has_prev']:
        pagination.append(f"[bold cyan](P)revious[/]")
    
    if paginated['has_next']:
        if paginated['has_prev']:
            pagination.append(" | ")
        pagination.append(f"[bold cyan](N)ext[/]")
    
    if pagination:
        console.print("\n" + "".join(pagination))
        console.print("\nPress [dim]Q[/] to quit")
        
        # Handle pagination input
        while True:
            try:
                key = input("\n> ").strip().lower()
                
                if key == 'q':
                    break
                elif key == 'p' and paginated['has_prev']:
                    display_paginated(
                        items=items,
                        columns=columns,
                        title=title,
                        page=paginated['page'] - 1,
                        per_page=per_page
                    )
                    break
                elif key == 'n' and paginated['has_next']:
                    display_paginated(
                        items=items,
                        columns=columns,
                        title=title,
                        page=paginated['page'] + 1,
                        per_page=per_page
                    )
                    break
                
            except (KeyboardInterrupt, EOFError):
                break

def validate_email(email: str) -> bool:
    """Validate an email address format."""
    import re
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate a phone number format."""
    import re
    # Simple validation - allows common formats like (123) 456-7890, 123-456-7890, 123.456.7890, etc.
    pattern = r'^\+?\d{0,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
    return bool(re.match(pattern, phone))

def get_password_strength(password: str) -> str:
    """
    Check the strength of a password.
    
    Returns:
        str: Strength level (weak, medium, strong)
    """
    import re
    
    # Check length
    if len(password) < 8:
        return "weak"
    
    # Check for uppercase, lowercase, numbers, and special characters
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[^A-Za-z0-9]', password))
    
    score = sum([has_upper, has_lower, has_digit, has_special])
    
    if score >= 3 and len(password) >= 12:
        return "strong"
    elif score >= 2 and len(password) >= 10:
        return "medium"
    else:
        return "weak"

def format_duration(seconds: int) -> str:
    """Format a duration in seconds to a human-readable string."""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 and days == 0:  # Only show minutes if less than a day
        parts.append(f"{minutes}m")
    if seconds > 0 and hours == 0 and days == 0:  # Only show seconds if less than an hour
        parts.append(f"{seconds}s")
    
    return " ".join(parts) if parts else "0s"

def progress_bar(iteration: int, total: int, length: int = 50, prefix: str = '', 
                suffix: str = '', fill: str = '█', empty_fill: str = '-') -> str:
    """
    Create a progress bar string.
    
    Args:
        iteration: Current iteration
        total: Total iterations
        length: Character length of the progress bar
        prefix: Prefix string
        suffix: Suffix string
        fill: Bar fill character
        empty_fill: Empty bar fill character
    
    Returns:
        Formatted progress bar string
    """
    percent = (iteration / float(total)) if total > 0 else 0
    filled_length = int(length * percent)
    bar = fill * filled_length + empty_fill * (length - filled_length)
    return f"\r{prefix} |{bar}| {percent:.1%} {suffix}"

# Common column definitions for tables
PRODUCT_COLUMNS = {
    'id': 'ID',
    'name': 'Name',
    'price': 'Price',
    'quantity_available': 'Available',
    'unit': 'Unit',
    'category': 'Category',
    'farmer_name': 'Farmer'
}

TRANSACTION_COLUMNS = {
    'id': 'ID',
    'created_at': 'Date',
    'item_count': 'Items',
    'total_amount': 'Total',
    'status': 'Status',
    'shipping_address': 'Shipping To'
}

USER_COLUMNS = {
    'id': 'ID',
    'email': 'Email',
    'full_name': 'Name',
    'role': 'Role',
    'is_active': 'Active',
    'created_at': 'Joined On'
}
