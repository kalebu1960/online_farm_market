"""
Product management commands for the Online Farm Market CLI.
"""
import click
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Session

from ..models.product import Product
from ..models.user import UserRole

# Create a command group for product-related commands
@click.group()
def products_group():
    """Manage products in the farm market."""
    pass

@products_group.command()
@click.option('--name', prompt='Product name', help='Name of the product')
@click.option('--description', prompt='Product description', help='Description of the product')
@click.option('--price', type=float, prompt='Price per unit', help='Price per unit')
@click.option('--quantity', type=int, prompt='Available quantity', help='Available quantity')
@click.option('--unit', prompt='Unit (e.g., kg, lb, each)', help='Unit of measurement')
@click.option('--category', help='Product category (e.g., vegetable, fruit, dairy)')
@click.option('--organic/--not-organic', default=False, help='Is the product organic?')
@click.pass_context
def add_product(ctx, name: str, description: str, price: float, quantity: int, 
               unit: str, category: str, organic: bool):
    """Add a new product to your farm's inventory (Farmers only)."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    user_id = ctx.obj.get('user_id')
    
    # Verify user is a farmer
    if ctx.obj.get('user_role') != UserRole.FARMER:
        console.print("[error]Only farmers can add products.[/]")
        return
    
    try:
        # Create new product
        product = Product(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            unit=unit,
            category=category,
            organic=organic,
            farmer_id=ctx.obj.get('farmer_id')
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        console.print(f"\n✅ [success]Product '{name}' added successfully![/]")
        console.print(f"   [info]ID:[/] {product.id}")
        
    except Exception as e:
        db.rollback()
        console.print(f"[error]Error adding product:[/] {str(e)}")

@products_group.command()
@click.option('--id', type=int, help='Filter by product ID')
@click.option('--name', help='Filter by product name')
@click.option('--category', help='Filter by category')
@click.option('--min-price', type=float, help='Minimum price')
@click.option('--max-price', type=float, help='Maximum price')
@click.option('--organic/--not-organic', default=None, help='Filter by organic status')
@click.pass_context
def list_products(ctx, id: Optional[int], name: Optional[str], category: Optional[str], 
                 min_price: Optional[float], max_price: Optional[float], organic: Optional[bool]):
    """List all available products with optional filters."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    
    # Start with base query
    query = db.query(Product)
    
    # Apply filters
    if id:
        query = query.filter(Product.id == id)
    if name:
        query = query.filter(Product.name.ilike(f'%{name}%'))
    if category:
        query = query.filter(Product.category.ilike(f'%{category}%'))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if organic is not None:
        query = query.filter(Product.organic == organic)
    
    # Execute query
    products = query.all()
    
    if not products:
        console.print("[info]No products found matching your criteria.[/]")
        return
    
    # Display results in a table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Price")
    table.add_column("Qty")
    table.add_column("Category")
    table.add_column("Organic")
    
    for product in products:
        table.add_row(
            str(product.id),
            product.name,
            f"${product.price:.2f}/{product.unit}",
            str(product.quantity),
            product.category or "N/A",
            "✅" if product.organic else "❌"
        )
    
    console.print("\n[bold]Available Products:[/]")
    console.print(table)

@products_group.command()
@click.argument('product_id', type=int)
@click.option('--name', help='New product name')
@click.option('--description', help='New description')
@click.option('--price', type=float, help='New price')
@click.option('--quantity', type=int, help='New quantity')
@click.option('--unit', help='New unit of measurement')
@click.option('--category', help='New category')
@click.option('--organic/--not-organic', is_flag=True, default=None, help='Update organic status')
@click.pass_context
def update_product(ctx, product_id: int, **updates):
    """Update product details (Farmers only)."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    
    # Verify user is a farmer
    if ctx.obj.get('user_role') != UserRole.FARMER:
        console.print("[error]Only farmers can update products.[/]")
        return
    
    # Remove None values from updates
    updates = {k: v for k, v in updates.items() if v is not None}
    
    if not updates:
        console.print("[warning]No updates provided.[/]")
        return
    
    try:
        # Get the product
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.farmer_id == ctx.obj.get('farmer_id')  # Only owner can update
        ).first()
        
        if not product:
            console.print(f"[error]Product with ID {product_id} not found or you don't have permission to update it.[/]")
            return
        
        # Update fields
        for key, value in updates.items():
            setattr(product, key, value)
        
        db.commit()
        db.refresh(product)
        
        console.print(f"\n✅ [success]Product '{product.name}' updated successfully![/]")
        
    except Exception as e:
        db.rollback()
        console.print(f"[error]Error updating product:[/] {str(e)}")

@products_group.command()
@click.argument('product_id', type=int)
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@click.pass_context
def remove_product(ctx, product_id: int, yes: bool):
    """Remove a product from your inventory (Farmers only)."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    user_id = ctx.obj.get('user_id')
    
    # Verify user is a farmer
    if ctx.obj.get('user_role') != UserRole.FARMER:
        console.print("[error]Only farmers can remove products.[/]")
        return
    
    try:
        # Get the product
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.farmer_id == ctx.obj.get('farmer_id')  # Only owner can delete
        ).first()
        
        if not product:
            console.print(f"[error]Product with ID {product_id} not found or you don't have permission to delete it.[/]")
            return
        
        # Confirm deletion
        if not yes:
            confirm = click.confirm(f"Are you sure you want to delete '{product.name}'?")
            if not confirm:
                console.print("[info]Operation cancelled.[/]")
                return
        
        # Delete the product
        db.delete(product)
        db.commit()
        
        console.print(f"\n✅ [success]Product '{product.name}' has been removed.[/]")
        
    except Exception as e:
        db.rollback()
        console.print(f"[error]Error removing product:[/] {str(e)}")

# Add the products group to the main CLI
products = products_group
