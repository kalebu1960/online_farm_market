"""merge product model updates

Revision ID: 6f7eb53ef170
Revises: 3829bd5d787d, 123456789abc
Create Date: 2025-08-29 20:16:00.218645+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f7eb53ef170'
down_revision: Union[str, Sequence[str], None] = ('3829bd5d787d', '123456789abc')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
