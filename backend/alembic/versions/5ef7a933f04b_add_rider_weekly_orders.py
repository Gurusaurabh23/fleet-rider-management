"""add_rider_weekly_orders

Revision ID: 5ef7a933f04b
Revises: 8a80de882d3d
Create Date: 2025-12-25 17:26:54.327258
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ef7a933f04b'
down_revision: Union[str, Sequence[str], None] = '8a80de882d3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rider_weekly_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "rider_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("completed_orders", sa.Integer(), nullable=False, default=0),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "rider_id",
            "week_start",
            name="uq_rider_weekly_orders_rider_week",
        ),
    )


def downgrade() -> None:
    op.drop_table("rider_weekly_orders")
