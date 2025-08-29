"""Update Product model for marketplace features

Revision ID: 0dd801543306
Revises: 37ad57533897
Create Date: 2025-08-29 19:51:13.493496+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0dd801543306'
down_revision: Union[str, Sequence[str], None] = '37ad57533897'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite doesn't support ALTER TABLE for some operations, so we need to:
    # 1. Create a new table with the updated schema
    # 2. Copy data from the old table to the new one
    # 3. Drop the old table
    # 4. Rename the new table to the original name
    
    # Create new table with updated schema
    op.create_table(
        'products_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('quantity', sa.String(length=50), nullable=False, server_default='1'),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='Other'),
        sa.Column('condition', sa.String(length=20), nullable=False, server_default='new'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='available'),
        sa.Column('location', sa.String(length=100), nullable=False, server_default='Not specified'),
        sa.Column('is_negotiable', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('image_urls', sa.Text(), nullable=True),
        sa.Column('farmer_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['farmer_id'], ['farmers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data from old table to new table
    op.execute('''
        INSERT INTO products_new (
            id, created_at, updated_at, title, description, price, quantity, 
            unit, category, condition, status, location, is_negotiable, 
            is_featured, views, farmer_id
        )
        SELECT 
            p.id, p.created_at, p.updated_at, 
            COALESCE(p.name, 'Untitled Product') as title,
            COALESCE(p.description, 'No description provided') as description,
            p.price,
            CAST(COALESCE(p.quantity_available, 1) AS TEXT) as quantity,
            p.unit,
            COALESCE(p.category, 'Other') as category,
            'new' as condition,
            'available' as status,
            'Not specified' as location,
            0 as is_negotiable,
            0 as is_featured,
            0 as views,
            p.farmer_id
        FROM products p
    ''')
    
    # Drop old table
    op.drop_table('products')
    
    # Rename new table to original name
    op.rename_table('products_new', 'products')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Create old table structure
    op.create_table(
        'products_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False, server_default='Product'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('quantity_available', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('is_organic', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('farmer_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['farmer_id'], ['farmers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data back to old table (losing some data in the process)
    op.execute('''
        INSERT INTO products_old (
            id, created_at, updated_at, name, description, price, 
            quantity_available, unit, category, is_organic, farmer_id
        )
        SELECT 
            p.id, p.created_at, p.updated_at, 
            p.title as name,
            p.description,
            p.price,
            CAST(p.quantity AS INTEGER) as quantity_available,
            p.unit,
            p.category,
            0 as is_organic,
            p.farmer_id
        FROM products p
    ''')
    
    # Drop new table
    op.drop_table('products')
    
    # Rename old table back to original name
    op.rename_table('products_old', 'products')
    # ### end Alembic commands ###
