"""Update Farmer model with contact and location fields

Revision ID: 37ad57533897
Revises: e2ce2f824c28
Create Date: 2025-08-29 19:49:53.853438+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37ad57533897'
down_revision: Union[str, Sequence[str], None] = 'e2ce2f824c28'
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
        'farmers_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('farm_name', sa.String(length=100), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('address', sa.String(length=200), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('zip_code', sa.String(length=20), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('whatsapp_number', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Copy data from old table to new table
    op.execute('''
        INSERT INTO farmers_new (id, created_at, updated_at, user_id, farm_name, bio, address, city, state, zip_code, phone_number)
        SELECT id, created_at, updated_at, user_id, farm_name, bio, 
               COALESCE(address, 'Not specified') as address,
               COALESCE(city, 'Not specified') as city,
               COALESCE(state, 'Not specified') as state,
               COALESCE(zip_code, '00000') as zip_code,
               'Not specified' as phone_number
        FROM farmers
    ''')
    
    # Drop old table
    op.drop_table('farmers')
    
    # Rename new table to original name
    op.rename_table('farmers_new', 'farmers')


def downgrade() -> None:
    """Downgrade schema."""
    # This is a simplified downgrade that will lose any new data
    # In a production environment, you'd want to properly migrate data back
    
    # Create old table structure
    op.create_table(
        'farmers_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('farm_name', sa.String(length=100), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('address', sa.String(length=200), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('zip_code', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Copy data back to old table (losing new columns' data)
    op.execute('''
        INSERT INTO farmers_old (id, created_at, updated_at, user_id, farm_name, bio, address, city, state, zip_code)
        SELECT id, created_at, updated_at, user_id, farm_name, bio, address, city, state, zip_code
        FROM farmers
    ''')
    
    # Drop new table
    op.drop_table('farmers')
    
    # Rename old table back to original name
    op.rename_table('farmers_old', 'farmers')
