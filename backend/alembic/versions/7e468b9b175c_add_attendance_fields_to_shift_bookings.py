"""add_attendance_fields_to_shift_bookings

Revision ID: 7e468b9b175c
Revises: 92f2edb910e2
Create Date: 2025-12-25 12:41:30.428975

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e468b9b175c'
down_revision: Union[str, Sequence[str], None] = '92f2edb910e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Columns already exist in DB
    pass


def downgrade():
    # No-op (columns already exist)
    pass
