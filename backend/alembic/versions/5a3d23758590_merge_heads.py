"""merge heads

Revision ID: 5a3d23758590
Revises: d6f8e81379c4, xxxxx
Create Date: 2025-12-21 15:46:51.296305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a3d23758590'
down_revision: Union[str, Sequence[str], None] = ('d6f8e81379c4', 'xxxxx')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
