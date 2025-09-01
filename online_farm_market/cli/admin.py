"""
Admin commands for the Online Farm Market CLI.
"""
import click
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Session

# Import models and utilities
from ..models import User, UserRole, Customer, Farmer, Product, Order, OrderStatus
from ..database import SessionLocal
from .main import cli

@cli.group()
@click.pass_context
def admin(ctx):
    """Administrative commands (requires admin privileges)."""
    # Check if user is admin
    if ctx.obj.get("user_role") != UserRole.ADMIN:
        console = ctx.obj["console"]
        console.print("[error]Error: This command requires administrator privileges.[/]")
        ctx.exit(1)

@admin.group()
def user():
    """User management commands."""
    pass

@user.command("list")
@click.option('--role', type=click.Choice(['all', 'customer', 'farmer', 'admin'], case_sensitive=False), 
              default='all', help='Filter users by role')
@click.option('--active/--inactive', 'is_active', default=None, help='Filter by active status')
@click.pass_context
def list_users(ctx, role: str, is_active: Optional[bool]):
    """List all users with optional filtering."""
    console = ctx.obj["console"]
    db = SessionLocal()
    
    try:
        query = db.query(User)
        
        # Apply filters
        if role != 'all':
            query = query.filter(User.role == UserRole(role.lower()))
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        users = query.order_by(User.created_at.desc()).all()
        
        if not users:
            console.print("[info]No users found.[/]")
            return
        
        # Create a table to display users
        table = Table(title="Users")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Email")
        table.add_column("Role")
        table.add_column("Active", justify="center")
        table.add_column("Joined", justify="right")
        
        for user in users:
            table.add_row(
                str(user.id),
                user.full_name,
                user.email,
                user.role.value.capitalize(),
                "✅" if user.is_active else "❌",
                user.created_at.strftime("%Y-%m-%d")
            )
        
        console.print(table)
        console.print(f"\nTotal users: {len(users)}")
        
    except Exception as e:
        console.print(f"[error]An error occurred: {str(e)}[/]")
    finally:
        db.close()

@user.command()
@click.argument('email')
@click.option('--role', type=click.Choice(['customer', 'farmer', 'admin'], case_sensitive=False), 
              required=True, help='User role')
@click.option('--full-name', required=True, help="User's full name")
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, 
              help="User's password")
@click.option('--phone', help="User's phone number")
@click.option('--active/--inactive', 'is_active', default=True, help='Account status')
@click.pass_context
def create(ctx, email: str, role: str, full_name: str, password: str, phone: str, is_active: bool):
    """Create a new user account."""
    console = ctx.obj["console"]
    db = SessionLocal()
    
    try:
        # Check if user already exists
        if User.get_by_email(db, email):
            console.print("[error]A user with this email already exists.[/]")
            return
        
        # Create the user
        user = User(
            email=email,
            full_name=full_name,
            phone_number=phone,
            role=UserRole(role.lower()),
            password=password,
            is_active=is_active
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create a customer or farmer profile based on role
        if role.lower() == 'customer':
            customer = Customer(
                user_id=user.id,
                shipping_address="",
                city="",
                state="",
                zip_code=""
            )
            db.add(customer)
        else:  # farmer or admin
            farmer = Farmer(
                user_id=user.id,
                farm_name=f"{full_name}'s Farm" if role.lower() == 'farmer' else "N/A",
                farm_description="",
                address="",
                city="",
                state="",
                zip_code=""
            )
            db.add(farmer)
        
        db.commit()
        
        console.print(f"\n✅ [success]User created successfully![/]")
        console.print(f"   Name: {user.full_name}")
        console.print(f"   Email: {user.email}")
        console.print(f"   Role: {user.role.value.capitalize()}")
        console.print(f"   Status: {'Active' if user.is_active else 'Inactive'}")
        
    except Exception as e:
        db.rollback()
        console.print(f"[error]An error occurred: {str(e)}[/]")
    finally:
        db.close()

@user.command()
@click.argument('user_id', type=int)
@click.option('--email', help="New email address")
@click.option('--full-name', help="New full name")
@click.option('--phone', help="New phone number")
@click.option('--role', type=click.Choice(['customer', 'farmer', 'admin'], case_sensitive=False), 
              help='New role')
@click.option('--active/--inactive', 'is_active', default=None, help='Account status')
@click.option('--password', help="New password (leave empty to keep current)")
@click.pass_context
def update(ctx, user_id: int, email: Optional[str], full_name: Optional[str], 
          phone: Optional[str], role: Optional[str], is_active: Optional[bool], 
          password: Optional[str]):
    """Update a user's information."""
    console = ctx.obj["console"]
    db = SessionLocal()
    
    try:
        user = db.query(User).get(user_id)
        if not user:
            console.print(f"[error]User with ID {user_id} not found.[/]")
            return
        
        # Update fields if provided
        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        if phone is not None:
            user.phone_number = phone
        if role is not None:
            user.role = UserRole(role.lower())
        if is_active is not None:
            user.is_active = is_active
        if password:
            user.set_password(password)
        
        db.commit()
        db.refresh(user)
        
        console.print(f"\n✅ [success]User updated successfully![/]")
        console.print(f"   Name: {user.full_name}")
        console.print(f"   Email: {user.email}")
        console.print(f"   Role: {user.role.value.capitalize()}")
        console.print(f"   Status: {'Active' if user.is_active else 'Inactive'}")
        
    except Exception as e:
        db.rollback()
        console.print(f"[error]An error occurred: {str(e)}[/]")
    finally:
        db.close()

@user.command()
@click.argument('user_id', type=int)
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def delete(ctx, user_id: int, confirm: bool):
    """Delete a user account."""
    console = ctx.obj["console"]
    
    if not confirm:
        if not click.confirm(f"Are you sure you want to delete user with ID {user_id}? This action cannot be undone."):
            console.print("[info]Operation cancelled.[/]")
            return
    
    db = SessionLocal()
    
    try:
        user = db.query(User).get(user_id)
        if not user:
            console.print(f"[error]User with ID {user_id} not found.[/]")
            return
        
        # Delete related records first (handled by cascade in the database)
        # Then delete the user
        db.delete(user)
        db.commit()
        
        console.print(f"\n✅ [success]User deleted successfully![/]")
        
    except Exception as e:
        db.rollback()
        console.print(f"[error]An error occurred: {str(e)}[/]")
    finally:
        db.close()

@admin.group()
def system():
    """System administration commands."""
    pass

@system.command()
@click.pass_context
def stats(ctx):
    """Display system statistics."""
    console = ctx.obj["console"]
    db = SessionLocal()
    
    try:
        from sqlalchemy import func
        
        # Get counts
        user_count = db.query(func.count(User.id)).scalar()
        customer_count = db.query(func.count(Customer.id)).scalar()
        farmer_count = db.query(func.count(Farmer.id)).scalar()
        product_count = db.query(func.count(Product.id)).scalar()
        order_count = db.query(func.count(Order.id)).scalar()
        
        # Get recent users
        recent_users = (
            db.query(User)
            .order_by(User.created_at.desc())
            .limit(5)
            .all()
        )
        
        # Get recent orders
        recent_orders = (
            db.query(Order)
            .order_by(Order.created_at.desc())
            .limit(5)
            .all()
        )
        
        # Display statistics
        console.print("\n[title]System Statistics[/]")
        console.print(f"\n[highlight]Users:[/] {user_count} total ({customer_count} customers, {farmer_count} farmers, {user_count - customer_count - farmer_count} others)")
        console.print(f"[highlight]Products:[/] {product_count}")
        console.print(f"[highlight]Orders:[/] {order_count}")
        
        # Display recent users
        console.print("\n[title]Recent Users[/]")
        if recent_users:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID", style="dim")
            table.add_column("Name")
            table.add_column("Email")
            table.add_column("Role")
            table.add_column("Joined")
            
            for user in recent_users:
                table.add_row(
                    str(user.id),
                    user.full_name,
                    user.email,
                    user.role.value.capitalize(),
                    user.created_at.strftime("%Y-%m-%d")
                )
            
            console.print(table)
        else:
            console.print("No users found.")
        
        # Display recent orders
        console.print("\n[title]Recent Orders[/]")
        if recent_orders:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID", style="dim")
            table.add_column("Customer")
            table.add_column("Amount")
            table.add_column("Status")
            table.add_column("Date")
            
            for order in recent_orders:
                customer_name = order.customer.user.full_name if order.customer and order.customer.user else "Unknown"
                table.add_row(
                    str(order.id),
                    customer_name,
                    f"${order.total_amount:.2f}",
                    order.status.value.capitalize(),
                    order.created_at.strftime("%Y-%m-%d")
                )
            
            console.print(table)
        else:
            console.print("No orders found.")
        
    except Exception as e:
        console.print(f"[error]An error occurred: {str(e)}[/]")
    finally:
        db.close()

@system.command()
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def reset_db(ctx, confirm: bool):
    """Reset the database (DANGER: This will delete all data!)."""
    console = ctx.obj["console"]
    
    if not confirm:
        if not click.confirm("\n[bold red]WARNING: This will delete ALL data in the database!\nAre you absolutely sure you want to continue?[/]"):
            console.print("[info]Operation cancelled.[/]")
            return
    
    from ..database import drop_db, init_db
    
    try:
        console.print("\n[warning]Dropping all database tables...[/]")
        drop_db()
        
        console.print("\n[info]Creating database schema...[/]")
        init_db()
        
        console.print("\n✅ [success]Database has been reset successfully![/]")
        
    except Exception as e:
        console.print(f"[error]An error occurred: {str(e)}[/]")
