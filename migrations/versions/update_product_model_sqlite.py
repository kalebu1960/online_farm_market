"""Update Product model for OLX-style marketplace

Revision ID: 123456789abc
Revises: 0dd801543306
Create Date: 2025-08-29 20:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '123456789abc'
down_revision = '0dd801543306'
branch_labels = None
depends_on = None

def upgrade():
    # Create a new table with the updated schema
    op.create_table(
        'products_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('title', sa.String(length=100), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('quantity', sa.String(50), nullable=False, server_default='1'),
        sa.Column('unit', sa.String(20), nullable=True),
        sa.Column('category', sa.String(50), nullable=False, server_default='Other'),
        sa.Column('condition', sa.String(20), nullable=False, server_default='new'),
        sa.Column('status', sa.String(20), nullable=False, server_default='available'),
        sa.Column('location', sa.String(100), nullable=False, server_default=''),
        sa.Column('is_negotiable', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('image_urls', sa.Text(), nullable=True),
        sa.Column('farmer_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['farmer_id'], ['farmers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data from old table to new table with default values
    op.execute('''
        INSERT INTO products_new (
            id, created_at, updated_at, title, description, price,
            quantity, unit, category, condition, status, location,
            is_negotiable, is_featured, views, farmer_id
        )
        SELECT 
            id, 
            COALESCE(created_at, CURRENT_TIMESTAMP) as created_at,
            COALESCE(created_at, CURRENT_TIMESTAMP) as updated_at,
            'Product ' || id as title,
            COALESCE(description, 'No description available') as description,
            COALESCE(price, 0.0) as price,
            '1' as quantity,
            COALESCE(unit, 'piece') as unit,
            COALESCE(category, 'Other') as category,
            'new' as condition,
            'available' as status,
            'Unknown' as location,
            0 as is_negotiable,
            0 as is_featured,
            0 as views,
            COALESCE(farmer_id, 1) as farmer_id
        FROM products
    ''')
    
    # Drop old table
    op.drop_table('products')
    
    # Rename new table to original name
    op.rename_table('products_new', 'products')
    
    # Create indexes
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)


def downgrade():
    # Create old table structure
    op.create_table(
        'products_old',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('created_at', sa.DATETIME(), nullable=True),
        sa.Column('updated_at', sa.DATETIME(), nullable=True),
        sa.Column('name', sa.VARCHAR(length=100), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('price', sa.NUMERIC(10, 2), nullable=False),
        sa.Column('quantity_available', sa.INTEGER(), nullable=True, server_default='0'),
        sa.Column('unit', sa.VARCHAR(20), nullable=True),
        sa.Column('category', sa.VARCHAR(50), nullable=True),
        sa.Column('is_organic', sa.BOOLEAN(), nullable=True, server_default='0'),
        sa.Column('farmer_id', sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(['farmer_id'], ['farmers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data back to old table (with potential data loss)
    op.execute('''
        INSERT INTO products_old (
            id, created_at, updated_at, name, description, price,
            quantity_available, unit, category, is_organic, farmer_id
        )
        SELECT 
            id, created_at, updated_at, 
            title as name,
            description,
            price,
            CAST(quantity AS INTEGER) as quantity_available,
            unit,
            category,
            CASE WHEN title LIKE '%organic%' OR description LIKE '%organic%' THEN 1 ELSE 0 END as is_organic,
            farmer_id
        FROM products
    ''')
    
    # Drop new table
    op.drop_table('products')
    
    # Rename old table to original name
    op.rename_table('products_old', 'products')
