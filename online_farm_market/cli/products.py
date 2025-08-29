"""
Product management commands for the Online Farm Market CLI.
"""
import click
from datetime import datetime
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.product import Product
from ..models.farmer import Farmer
from ..models.user import UserRole, User

# Common categories for farm products
PRODUCT_CATEGORIES = [
    'Vegetables', 'Fruits', 'Grains', 'Dairy', 'Meat', 'Poultry',
    'Seafood', 'Herbs', 'Nuts', 'Honey', 'Eggs', 'Mushrooms',
    'Processed Foods', 'Beverages', 'Other'
]

# Common conditions for products
PRODUCT_CONDITIONS = ['new', 'used', 'refurbished']

# Common units for products
PRODUCT_UNITS = [
    'kg', 'g', 'lb', 'oz', 'liter', 'ml', 'piece', 'dozen', 'bunch',
    'pack', 'box', 'bottle', 'jar', 'bag', 'sack'
]

def display_product_details(product: Product, console: Console) -> None:
    """Display detailed information about a product."""
    # Product header
    console.print(f"\n[bold]{product.title}[/]")
    console.print(f"[dim]Posted on: {product.created_at.strftime('%Y-%m-%d')}")
    console.print(f"[dim]Views: {product.views}")
    
    # Price and status
    price_text = Text(f"\n💰 Price: ${product.price:.2f}", style="bold green")
    if product.is_negotiable:
        price_text.append(" (Negotiable)", style="italic")
    console.print(price_text)
    
    # Status
    status_style = "green" if product.status == "available" else "red"
    console.print(f"Status: [{status_style}]{product.status.capitalize()}[/]")
    
    # Quantity and condition
    console.print(f"\n📦 Quantity: {product.quantity}" + (f" {product.unit}" if product.unit else ""))
    console.print(f"🔄 Condition: {product.condition.capitalize()}")
    
    # Category and location
    console.print(f"\n🏷️  Category: {product.category}")
    console.print(f"📍 Location: {product.location}")
    
    # Description
    console.print("\n📝 Description:")
    console.print(Panel(product.description, width=80))
    
    # Seller information
    seller = product.farmer
    console.print("\n👤 Seller Information:")
    console.print(f"  🏠 {seller.farm_name}")
    console.print(f"  📞 {seller.phone_number}")
    if seller.whatsapp_number:
        console.print(f"  💬 WhatsApp: {seller.whatsapp_number}")
    if seller.email:
        console.print(f"  ✉️  {seller.email}")
    console.print(f"  📍 {seller.address}, {seller.city}, {seller.state} {seller.zip_code}")
    
    # Images (placeholder)
    if product.image_urls:
        console.print("\n🖼️  [info]This product has images (view in app)[/]")
    else:
        console.print("\n📷 [dim]No images available[/]")
    
    # Action buttons (for CLI)
    console.print("\n[bold]Actions:[/] [dim]Contact seller for more details[/]")
    console.print("  • Call: [bold]" + seller.phone_number + "[/]")
    if seller.whatsapp_number:
        console.print("  • WhatsApp: [bold]" + seller.whatsapp_number + "[/]")

# Create a command group for product-related commands
@click.group()
def products_group():
    """Manage products in the farm market."""
    pass

@products_group.command()
@click.option('--title', prompt='Product title', help='Title of the product listing')
@click.option('--description', prompt='Detailed description', help='Detailed description of the product')
@click.option('--price', type=float, prompt='Price', help='Price (in your local currency)')
@click.option('--quantity', prompt='Quantity available', help='E.g., 5 kg, 10 pieces, etc.')
@click.option('--category', type=click.Choice(PRODUCT_CATEGORIES, case_sensitive=False), 
              prompt='Select category', help='Product category')
@click.option('--condition', type=click.Choice(PRODUCT_CONDITIONS, case_sensitive=False), 
              default='new', show_default=True, help='Product condition')
@click.option('--location', prompt='Location (city/area)', help='Where is the product located?')
@click.option('--negotiable/--not-negotiable', default=False, 
              help='Is the price negotiable?')
@click.option('--unit', type=click.Choice(PRODUCT_UNITS, case_sensitive=False), 
              help='Unit of measurement (optional if included in quantity)')
@click.pass_context
def add_product(ctx, title: str, description: str, price: float, quantity: str, 
               category: str, condition: str, location: str, negotiable: bool, unit: Optional[str] = None):
    """Create a new product listing (Farmers only)."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    
    # Verify user is a farmer
    if ctx.obj.get('user_role') != UserRole.FARMER:
        console.print("[error]Only farmers can create product listings.[/]")
        return
    
    try:
        # Get farmer profile
        farmer = db.query(Farmer).filter(Farmer.user_id == ctx.obj.get('user_id')).first()
        if not farmer:
            console.print("[error]Farmer profile not found. Please complete your profile first.[/]")
            return
        
        # Create new product
        product = Product(
            title=title,
            description=description,
            price=price,
            quantity=quantity,
            unit=unit,
            category=category,
            condition=condition,
            status="available",
            location=location,
            is_negotiable=negotiable,
            is_featured=False,  # Can be set by admin later
            views=0,
            farmer_id=farmer.id
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        console.print("\n✅ [success]Product listing created successfully![/]")
        console.print(f"   [info]Listing ID:[/] {product.id}")
        console.print("\n[bold]Next steps:[/]")
        console.print("• Share your listing with potential buyers")
        console.print("• Be ready to respond to inquiries")
        console.print("• Update the status when sold")
        
    except Exception as e:
        db.rollback()
        console.print(f"[error]Error creating product listing:[/] {str(e)}")

@products_group.command()
@click.option('--search', '-s', help='Search in title and description')
@click.option('--category', type=click.Choice(PRODUCT_CATEGORIES, case_sensitive=False), 
              help='Filter by category')
@click.option('--location', help='Filter by location (city/area)')
@click.option('--min-price', type=float, help='Minimum price')
@click.option('--max-price', type=float, help='Maximum price')
@click.option('--condition', type=click.Choice(PRODUCT_CONDITIONS, case_sensitive=False),
              help='Filter by condition')
@click.option('--sort', type=click.Choice(['newest', 'price-low', 'price-high', 'popular']), 
              default='newest', help='Sort results')
@click.option('--limit', type=int, default=20, help='Maximum number of results to show')
@click.option('--id', type=int, help='View details of a specific product by ID')
@click.pass_context
def list_products(ctx, search: Optional[str], category: Optional[str], location: Optional[str],
                 min_price: Optional[float], max_price: Optional[float], condition: Optional[str],
                 sort: str, limit: int, id: Optional[int]):
    """Browse product listings with filters and search."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    
    # Start with base query
    query = db.query(Product).join(Farmer).filter(Product.status == 'available')
    
    # Apply filters
    if id:
        # Show detailed view for a single product
        product = query.filter(Product.id == id).first()
        if not product:
            console.print("[error]Product not found or no longer available.[/]")
            return
        
        # Increment view count
        product.views += 1
        db.commit()
        
        # Display detailed view
        display_product_details(product, console)
        return
    
    if search:
        search_terms = f'%{search}%'
        query = query.filter(
            or_(
                Product.title.ilike(search_terms),
                Product.description.ilike(search_terms)
            )
        )
    
    if category:
        query = query.filter(Product.category.ilike(f'%{category}%'))
    
    if location:
        location_terms = f'%{location}%'
        query = query.filter(
            or_(
                Product.location.ilike(location_terms),
                Farmer.city.ilike(location_terms),
                Farmer.state.ilike(location_terms)
            )
        )
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if condition:
        query = query.filter(Product.condition == condition)
    
    # Apply sorting
    if sort == 'newest':
        query = query.order_by(Product.created_at.desc())
    elif sort == 'price-low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price-high':
        query = query.order_by(Product.price.desc())
    elif sort == 'popular':
        query = query.order_by(Product.views.desc())
    
    # Execute query
    products = query.limit(limit).all()
    
    if not products:
        console.print("\n[info]No products found matching your criteria.[/]")
        console.print("Try adjusting your search filters.")
        return
    
    # Display results in a table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Title", width=30)
    table.add_column("Price", width=15)
    table.add_column("Location", width=20)
    table.add_column("Posted", width=12)
    table.add_column("Views", width=8, justify="right")
    
    for product in products:
        price_text = f"${product.price:,.2f}"
        if product.is_negotiable:
            price_text += " 🏷️"
        
        table.add_row(
            str(product.id),
            product.title[:28] + ("..." if len(product.title) > 28 else ""),
            price_text,
            product.location,
            product.created_at.strftime('%b %d'),
            str(product.views)
        )
    
    console.print(f"\n[bold]📦 Found {len(products)} product{'s' if len(products) != 1 else ''}:[/]")
    console.print(table)
    console.print("\n[dim]Tip: Use 'product view <ID>' to see full details and contact information.[/]")

@products_group.command()
@click.argument('product_id', type=int)
@click.pass_context
def view_product(ctx, product_id: int):
    """View detailed information about a product."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    
    # Get the product with farmer details
    product = db.query(Product).join(Farmer).filter(Product.id == product_id).first()
    
    if not product:
        console.print("[error]Product not found or no longer available.[/]")
        return
    
    # Increment view count
    product.views += 1
    db.commit()
    
    # Display detailed view
    display_product_details(product, console)

@products_group.command()
@click.argument('product_id', type=int)
@click.option('--title', help='New title for the listing')
@click.option('--description', help='New description')
@click.option('--price', type=float, help='New price')
@click.option('--quantity', help='New quantity (e.g., 5 kg, 10 pieces)')
@click.option('--category', type=click.Choice(PRODUCT_CATEGORIES, case_sensitive=False), help='New category')
@click.option('--condition', type=click.Choice(PRODUCT_CONDITIONS, case_sensitive=False), help='Product condition')
@click.option('--location', help='New location (city/area)')
@click.option('--status', type=click.Choice(['available', 'sold', 'reserved']), help='Update listing status')
@click.option('--negotiable/--not-negotiable', is_flag=None, default=None, help='Is the price negotiable?')
@click.option('--unit', type=click.Choice(PRODUCT_UNITS, case_sensitive=False), help='Unit of measurement')
@click.pass_context
def update_product(ctx, product_id: int, **updates):
    """Update your product listing (Farmers only)."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    
    # Verify user is a farmer
    if ctx.obj.get('user_role') != UserRole.FARMER:
        console.print("[error]Only farmers can update product listings.[/]")
        return
    
    # Remove None values from updates
    updates = {k: v for k, v in updates.items() if v is not None}
    
    if not updates:
        console.print("[warning]No updates provided. Use --help to see available options.[/]")
        return
    
    try:
        # Get the product
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.farmer_id == ctx.obj.get('farmer_id')  # Only owner can update
        ).first()
        
        if not product:
            console.print(f"[error]Listing with ID {product_id} not found or you don't have permission to update it.[/]")
            return
        
        # Update fields
        for key, value in updates.items():
            setattr(product, key, value)
        
        product.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(product)
        
        console.print("\n✅ [success]Listing updated successfully![/]")
        display_product_details(product, console)
        
    except Exception as e:
        db.rollback()
        console.print(f"[error]Error updating listing:[/] {str(e)}")

@products_group.command()
@click.argument('product_id', type=int)
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@click.pass_context
def remove_product(ctx, product_id: int, yes: bool):
    """Remove a product listing (Farmers only)."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    
    # Verify user is a farmer
    if ctx.obj.get('user_role') != UserRole.FARMER:
        console.print("[error]Only farmers can remove product listings.[/]")
        return
    
    try:
        # Get the product with farmer details
        product = db.query(Product).join(Farmer).filter(
            Product.id == product_id,
            Product.farmer_id == ctx.obj.get('farmer_id')  # Only owner can delete
        ).first()
        
        if not product:
            console.print(f"[error]Listing with ID {product_id} not found or you don't have permission to remove it.[/]")
            return
        
        if not yes:
            console.print(f"\n[warning]Are you sure you want to delete your listing for '{product.title}'?[/]")
            if not click.confirm("This action cannot be undone. Continue?"):
                console.print("[info]Operation cancelled.[/]")
                return
        
        db.delete(product)
        db.commit()
        
        console.print(f"\n✅ [success]Your listing for '{product.title}' has been removed.[/]")
        
    except Exception as e:
        db.rollback()
        console.print(f"[error]Error removing listing:[/] {str(e)}")

@products_group.command()
@click.pass_context
def my_listings(ctx):
    """View and manage your product listings (Farmers only)."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    
    # Verify user is a farmer
    if ctx.obj.get('user_role') != UserRole.FARMER:
        console.print("[error]Only farmers can manage product listings.[/]")
        return
    
    try:
        # Get farmer's products
        products = db.query(Product).filter(
            Product.farmer_id == ctx.obj.get('farmer_id')
        ).order_by(Product.updated_at.desc()).all()
        
        if not products:
            console.print("\n[info]You don't have any active listings.[/]")
            console.print("Use 'product add' to create your first listing.")
            return
        
        # Display listings in a table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=8)
        table.add_column("Title", width=30)
        table.add_column("Price", width=15)
        table.add_column("Status", width=12)
        table.add_column("Views", width=8, justify="right")
        table.add_column("Last Updated", width=12)
        
        for product in products:
            status_style = "green" if product.status == "available" else "yellow" if product.status == "reserved" else "red"
            status_text = f"[{status_style}]{product.status.capitalize()}[/]"
            
            price_text = f"${product.price:,.2f}"
            if product.is_negotiable:
                price_text += " 🏷️"
            
            table.add_row(
                str(product.id),
                product.title[:28] + ("..." if len(product.title) > 28 else ""),
                price_text,
                status_text,
                str(product.views),
                product.updated_at.strftime('%b %d')
            )
        
        console.print("\n[bold]📋 Your Listings:[/]")
        console.print(table)
        console.print("\n[dim]Use 'product view <ID>' to see details, 'product update <ID>' to edit, or 'product remove <ID>' to delete.[/]")
        
    except Exception as e:
        console.print(f"[error]Error retrieving your listings:[/] {str(e)}")

# Add the products group to the main CLI
products = products_group
