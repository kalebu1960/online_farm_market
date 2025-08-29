"""
Transaction and order management commands for the Online Farm Market CLI.
"""
import click
from datetime import datetime
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Session

from ..models.transaction import Transaction, TransactionStatus, TransactionItem
from ..models.product import Product
from ..models.user import UserRole

# Create a command group for transaction-related commands
@click.group()
def transactions_group():
    """Manage orders and transactions in the farm market."""
    pass

# Helper function to display transaction details
def display_transaction_details(transaction: Transaction) -> None:
    """Display detailed information about a transaction."""
    console = Console()
    
    # Transaction header
    console.print(f"\n[bold]Order #{transaction.id}[/]")
    console.print(f"Status: [bold]{transaction.status.value}[/]")
    console.print(f"Date: {transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Customer information
    console.print("\n[b]Customer:[/b]")
    console.print(f"  {transaction.customer.user.full_name}")
    console.print(f"  {transaction.shipping_address or 'No shipping address provided'}")
    
    # Items table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Product", style="dim")
    table.add_column("Qty")
    table.add_column("Price")
    table.add_column("Total")
    
    for item in transaction.items:
        table.add_row(
            item.product.name,
            str(item.quantity),
            f"${item.unit_price:.2f}",
            f"${item.total_price:.2f}"
        )
    
    console.print("\n[b]Order Items:[/b]")
    console.print(table)
    
    # Totals
    console.print(f"\n[b]Subtotal:[/b] ${transaction.subtotal:.2f}")
    console.print(f"[b]Shipping:[/b] ${transaction.shipping_cost:.2f}")
    console.print(f"[b]Tax:[/b] ${transaction.tax_amount:.2f}")
    console.print(f"[b]Total:[/b] [bold]${transaction.total_amount:.2f}[/]")
    
    # Payment information
    if transaction.payment_status:
        console.print(f"\n[b]Payment Status:[/b] {transaction.payment_status}")
    
    # Tracking information
    if transaction.tracking_number:
        console.print(f"\n[b]Tracking Number:[/b] {transaction.tracking_number}")

# Authentication decorator
def require_auth(func):
    """Decorator to ensure user is authenticated."""
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        if 'user_id' not in ctx.obj:
            ctx.obj['console'].print("[error]You must be logged in to perform this action.[/]")
            ctx.exit(1)
        return ctx.invoke(func, ctx, *args, **kwargs)
    return wrapper

@transactions_group.command()
@require_auth
@click.option('--status', type=click.Choice([s.value for s in TransactionStatus]), 
              help='Filter by order status')
@click.option('--limit', type=int, default=10, help='Maximum number of orders to show')
@click.pass_context
def list_orders(ctx, status: Optional[str], limit: int):
    """List your orders with optional status filter."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    user_id = ctx.obj['user_id']
    
    # Build query
    query = db.query(Transaction).filter(Transaction.customer_id == user_id)
    
    if status:
        query = query.filter(Transaction.status == TransactionStatus(status))
    
    # Order by creation date (newest first)
    orders = query.order_by(Transaction.created_at.desc()).limit(limit).all()
    
    if not orders:
        console.print("[info]No orders found.[/]")
        return
    
    # Display orders in a table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Order #", style="dim")
    table.add_column("Date")
    table.add_column("Status")
    table.add_column("Items")
    table.add_column("Total")
    
    for order in orders:
        table.add_row(
            str(order.id),
            order.created_at.strftime('%Y-%m-%d'),
            order.status.value,
            str(len(order.items)),
            f"${order.total_amount:.2f}"
        )
    
    console.print(f"\n[bold]Your Orders:[/]")
    console.print(table)

@transactions_group.command()
@require_auth
@click.argument('order_id', type=int)
@click.pass_context
def view_order(ctx, order_id: int):
    """View details of a specific order."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    user_id = ctx.obj['user_id']
    
    # Get the order
    order = db.query(Transaction).filter(
        Transaction.id == order_id,
        Transaction.customer_id == user_id
    ).first()
    
    if not order:
        console.print(f"[error]Order #{order_id} not found or you don't have permission to view it.[/]")
        return
    
    # Display order details
    display_transaction_details(order)

@transactions_group.command()
@require_auth
@click.argument('product_id', type=int)
@click.option('--quantity', type=int, default=1, help='Quantity to order')
@click.option('--shipping-address', help='Shipping address for this order')
@click.option('--notes', help='Any additional notes for the order')
@click.pass_context
def place_order(ctx, product_id: int, quantity: int, shipping_address: Optional[str], notes: Optional[str]):
    """Place a new order for a product."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    user_id = ctx.obj['user_id']
    
    # Verify customer profile exists
    customer = db.query(Customer).filter(Customer.user_id == user_id).first()
    if not customer:
        console.print("[error]Customer profile not found. Please complete your profile first.[/]")
        return
    
    # Get the product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        console.print("[error]Product not found.[/]")
        return
    
    # Check product availability
    if product.quantity < quantity:
        console.print(f"[error]Insufficient stock. Only {product.quantity} available.[/]")
        return
    
    try:
        # Create transaction
        transaction = Transaction(
            customer_id=customer.id,
            farmer_id=product.farmer_id,
            status=TransactionStatus.PENDING,
            subtotal=product.price * quantity,
            tax_amount=0,  # Simplified for this example
            shipping_cost=0,  # Simplified for this example
            total_amount=product.price * quantity,
            shipping_address=shipping_address,
            notes=notes,
            items=[
                TransactionItem(
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.price,
                    total_price=product.price * quantity
                )
            ]
        )
        
        # Update product quantity
        product.quantity -= quantity
        
        # Save to database
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        console.print("\n✅ [success]Order placed successfully![/]")
        console.print(f"[info]Order #:[/] {transaction.id}")
        console.print(f"[info]Total:[/] ${transaction.total_amount:.2f}")
        
    except Exception as e:
        db.rollback()
        console.print(f"[error]Error placing order:[/] {str(e)}")

@transactions_group.command()
@require_auth
@click.argument('order_id', type=int)
@click.option('--status', type=click.Choice([s.value for s in TransactionStatus]), 
              required=True, help='New status for the order')
@click.option('--tracking-number', help='Tracking number (required for shipped status)')
@click.pass_context
def update_status(ctx, order_id: int, status: str, tracking_number: Optional[str]):
    """Update the status of an order (Farmers only)."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    
    # Verify user is a farmer
    if ctx.obj.get('user_role') != UserRole.FARMER:
        console.print("[error]Only farmers can update order status.[/]")
        return
    
    farmer_id = ctx.obj.get('farmer_id')
    if not farmer_id:
        console.print("[error]Farmer profile not found.[/]")
        return
    
    # Get the order
    order = db.query(Transaction).filter(
        Transaction.id == order_id,
        Transaction.farmer_id == farmer_id
    ).first()
    
    if not order:
        console.print(f"[error]Order #{order_id} not found or you don't have permission to update it.[/]")
        return
    
    # Validate status transition
    new_status = TransactionStatus(status)
    
    # Check if tracking number is provided when status is SHIPPED
    if new_status == TransactionStatus.SHIPPED and not tracking_number:
        console.print("[error]Tracking number is required when status is 'shipped'.[/]")
        return
    
    try:
        # Update order status
        order.status = new_status
        
        # Update tracking number if provided
        if tracking_number:
            order.tracking_number = tracking_number
        
        # Add status history
        order.status_history = order.status_history or []
        order.status_history.append({
            'status': new_status.value,
            'timestamp': datetime.utcnow().isoformat(),
            'notes': f'Status updated by farmer'
        })
        
        db.commit()
        db.refresh(order)
        
        console.print(f"\n✅ [success]Order #{order_id} status updated to '{status}'.[/]")
        
        # Notify customer (simplified for this example)
        if new_status == TransactionStatus.SHIPPED and tracking_number:
            console.print(f"[info]Tracking number:[/] {tracking_number}")
        
    except Exception as e:
        db.rollback()
        console.print(f"[error]Error updating order status:[/] {str(e)}")

# Add commands to the transactions group
transactions_group.add_command(list_orders, name="list")
transactions_group.add_command(view_order, name="view")
transactions_group.add_command(place_order, name="place")
transactions_group.add_command(update_status, name="update-status")

# Add the transactions group to the main CLI
transactions = transactions_group
