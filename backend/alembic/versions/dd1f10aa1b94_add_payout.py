"""add payout + hourly_rate

Revision ID: dd1f10aa1b94
Revises: 1518e6491f8b
Create Date: 2025-12-22 14:17:10.929438
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'dd1f10aa1b94'
down_revision: Union[str, Sequence[str], None] = '1518e6491f8b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # ---- add hourly_rate to users if missing ----
    result = conn.execute(
        sa.text("""
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_name='users' AND column_name='hourly_rate'
        """)
    ).fetchone()

    if not result:
        op.add_column('users', sa.Column('hourly_rate', sa.Float(), nullable=True))

    # ---- add payout to shifts if missing ----
    result2 = conn.execute(
        sa.text("""
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_name='shifts' AND column_name='payout'
        """)
    ).fetchone()

    if not result2:
        op.add_column('shifts', sa.Column('payout', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('shifts', 'payout')
    op.drop_column('users', 'hourly_rate')
