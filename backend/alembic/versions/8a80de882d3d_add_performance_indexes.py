"""add_performance_indexes

Revision ID: 8a80de882d3d
Revises: 7e468b9b175c
Create Date: 2025-12-25 13:16:26.120361

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a80de882d3d'
down_revision: Union[str, Sequence[str], None] = '7e468b9b175c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # GPS lookups
    op.create_index(
        "idx_gps_rider_timestamp",
        "gps_locations",
        ["rider_id", "timestamp"],
    )

    # Shift queries
    op.create_index(
        "idx_shift_rider_date",
        "shift_bookings",
        ["rider_id", "date"],
    )

    op.create_index(
        "idx_shift_attendance",
        "shift_bookings",
        ["attendance_status"],
    )

    # Payroll queries
    op.create_index(
        "idx_payroll_rider_date",
        "payroll",
        ["rider_id", "date"],
    )


def downgrade():
    op.drop_index("idx_gps_rider_timestamp", table_name="gps_locations")
    op.drop_index("idx_shift_rider_date", table_name="shift_bookings")
    op.drop_index("idx_shift_attendance", table_name="shift_bookings")
    op.drop_index("idx_payroll_rider_date", table_name="payroll")
