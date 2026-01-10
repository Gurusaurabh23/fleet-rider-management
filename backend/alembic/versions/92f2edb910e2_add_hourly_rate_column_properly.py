"""add hourly_rate column properly

Revision ID: 92f2edb910e2
Revises: 51c2dc6532f6
Create Date: 2025-12-22 15:34:21.803121
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92f2edb910e2'
down_revision: Union[str, Sequence[str], None] = '51c2dc6532f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add hourly_rate column to users if not exists."""
    op.add_column(
        'users',
        sa.Column('hourly_rate', sa.Float(), nullable=True)
    )


def downgrade() -> None:
    """Remove hourly_rate column."""
    op.drop_column('users', 'hourly_rate')
