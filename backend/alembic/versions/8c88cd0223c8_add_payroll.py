"""add payroll

Revision ID: 8c88cd0223c8
Revises: 7b992c539189
Create Date: 2025-12-21 03:02:10.766213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c88cd0223c8'
down_revision: Union[str, Sequence[str], None] = '7b992c539189'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
