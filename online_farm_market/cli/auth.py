"""
Authentication and user management commands for the Online Farm Market CLI.
"""
import click
from typing import Optional
from getpass import getpass
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Session

from ..models.user import User, UserRole
from ..models.farmer import Farmer
from ..models.customer import Customer

def get_current_user(db: Session, user_id: int) -> Optional[User]:
    """Helper function to get the current user."""
    return db.query(User).filter(User.id == user_id).first()

def require_auth(f):
    """Decorator to ensure the user is authenticated."""
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context()
        user_id = ctx.obj.get('user_id')
        
        if not user_id:
            ctx.fail("You must be logged in to use this command. Use 'login' first.")
        
        return f(*args, **kwargs)
    return wrapper

@click.group()
def auth_group():
    """Authentication and user management commands."""
    pass

@auth_group.command()
@click.option('--email', prompt='Email', help='Your email address')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Your password')
@click.option('--full-name', prompt='Full Name', help='Your full name')
@click.option('--phone', prompt='Phone Number', help='Your phone number')
@click.option('--role', type=click.Choice(['customer', 'farmer'], case_sensitive=False), default='customer', help='User role')
@click.pass_context
def register(ctx, email: str, password: str, full_name: str, phone: str, role: str):
    """Register a new user account."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    
    # Check if user already exists
    if User.get_by_email(db, email):
        console.print(f"[error]Error:[/] A user with email {email} already exists.")
        return
    
    try:
        # Create user
        user = User.create(
            db=db,
            email=email,
            password=password,
            full_name=full_name,
            phone_number=phone,
            role=UserRole(role)
        )
        
        # Create role-specific profile
        if role == 'farmer':
            farmer = Farmer.create(
                db=db,
                user_id=user.id,
                farm_name=f"{full_name}'s Farm"
            )
            console.print(f"\n✅ [success]Farmer account created successfully![/]")
            console.print(f"   Farm Name: {farmer.farm_name}")
        else:
            customer = Customer.create(
                db=db,
                user_id=user.id
            )
            console.print("\n✅ [success]Customer account created successfully![/]")
        
        console.print(f"   Email: {user.email}")
        console.print("\nYou can now log in using 'login' command.")
        
    except Exception as e:
        db.rollback()
        console.print(f"[error]Error creating account:[/] {str(e)}")

@auth_group.command()
@click.option('--email', prompt='Email', help='Your email address')
@click.option('--password', prompt=True, hide_input=True, help='Your password')
@click.pass_context
def login(ctx, email: str, password: str):
    """Log in to your account."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    
    user = User.get_by_email(db, email)
    
    if not user or not user.verify_password(password):
        console.print("[error]Invalid email or password.[/]")
        return
    
    if not user.is_active:
        console.print("[error]This account has been deactivated. Please contact support.[/]")
        return
    
    # Store user ID in context for other commands
    ctx.obj['user_id'] = user.id
    ctx.obj['user_role'] = user.role
    
    # Load additional user data based on role
    if user.role == UserRole.FARMER:
        farmer = Farmer.get_by_user_id(db, user.id)
        if farmer:
            ctx.obj['farmer_id'] = farmer.id
    elif user.role == UserRole.CUSTOMER:
        customer = Customer.get_by_user_id(db, user.id)
        if customer:
            ctx.obj['customer_id'] = customer.id
    
    console.print(f"\n✅ [success]Welcome back, {user.full_name}![/]")
    console.print(f"   Role: {user.role.value.capitalize()}")
    
    # Show quick stats or menu based on role
    if user.role == UserRole.FARMER:
        console.print("\n[title]Farmer Dashboard[/]")
        # Add farmer-specific stats here
    else:
        console.print("\n[title]Customer Dashboard[/]")
        # Add customer-specific stats here

@auth_group.command()
@click.pass_context
def profile(ctx):
    """View your profile information."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    user_id = ctx.obj.get('user_id')
    
    if not user_id:
        console.print("[error]You must be logged in to view your profile.[/]")
        return
    
    user = get_current_user(db, user_id)
    if not user:
        console.print("[error]User not found.[/]")
        return
    
    # Create a table to display profile information
    table = Table(title="\n👤 Your Profile", show_header=False, box=None)
    table.add_column("", style="cyan", width=20)
    table.add_column("")
    
    table.add_row("Name", user.full_name)
    table.add_row("Email", user.email)
    table.add_row("Phone", user.phone_number or "Not provided")
    table.add_row("Role", user.role.value.capitalize())
    table.add_row("Status", "Active" if user.is_active else "Inactive")
    table.add_row("Member Since", user.created_at.strftime("%B %d, %Y"))
    
    console.print(table)
    
    # Show role-specific information
    if user.role == UserRole.FARMER:
        farmer = Farmer.get_by_user_id(db, user_id)
        if farmer:
            console.print("\n[title]Farm Information[/]")
            farm_table = Table(show_header=False, box=None)
            farm_table.add_column("", style="cyan", width=20)
            farm_table.add_column("")
            
            farm_table.add_row("Farm Name", farmer.farm_name)
            if farmer.bio:
                farm_table.add_row("Bio", farmer.bio)
            if farmer.address:
                farm_table.add_row("Address", f"{farmer.address}, {farmer.city}, {farmer.state} {farmer.zip_code}")
                
            console.print(farm_table)
    
    elif user.role == UserRole.CUSTOMER:
        customer = Customer.get_by_user_id(db, user_id)
        if customer and (customer.shipping_address or customer.city or customer.state):
            console.print("\n[title]Shipping Information[/]")
            shipping_table = Table(show_header=False, box=None)
            shipping_table.add_column("", style="cyan", width=20)
            shipping_table.add_column("")
            
            if customer.shipping_address:
                shipping_table.add_row("Address", customer.shipping_address)
            if customer.city or customer.state or customer.zip_code:
                location = ", ".join(filter(None, [customer.city, customer.state, customer.zip_code]))
                shipping_table.add_row("Location", location)
                
            console.print(shipping_table)

@auth_group.command()
@click.option('--current-password', prompt=True, hide_input=True, help='Your current password')
@click.option('--new-password', prompt=True, hide_input=True, confirmation_prompt=True, help='Your new password')
@click.pass_context
def change_password(ctx, current_password: str, new_password: str):
    """Change your account password."""
    db = ctx.obj['db']
    console = ctx.obj['console']
    user_id = ctx.obj.get('user_id')
    
    if not user_id:
        console.print("[error]You must be logged in to change your password.[/]")
        return
    
    user = get_current_user(db, user_id)
    if not user:
        console.print("[error]User not found.[/]")
        return
    
    if not user.verify_password(current_password):
        console.print("[error]Current password is incorrect.[/]")
        return
    
    try:
        user.hashed_password = User.hash_password(new_password)
        db.commit()
        console.print("\n✅ [success]Password changed successfully![/]")
    except Exception as e:
        db.rollback()
        console.print(f"[error]Error changing password:[/] {str(e)}")

@auth_group.command()
@click.pass_context
def logout(ctx):
    """Log out of your account."""
    if 'user_id' in ctx.obj:
        del ctx.obj['user_id']
    if 'user_role' in ctx.obj:
        del ctx.obj['user_role']
    if 'farmer_id' in ctx.obj:
        del ctx.obj['farmer_id']
    if 'customer_id' in ctx.obj:
        del ctx.obj['customer_id']
    
    ctx.obj['console'].print("\n👋 [success]You have been logged out.[/]")

# Add commands to the auth group
auth_group.add_command(register)
auth_group.add_command(login)
auth_group.add_command(profile)
auth_group.add_command(change_password)
auth_group.add_command(logout)
