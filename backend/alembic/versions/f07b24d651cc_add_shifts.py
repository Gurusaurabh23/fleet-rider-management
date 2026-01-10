"""add shifts

Revision ID: f07b24d651cc
Revises: 92e9e489bfd5
Create Date: 2025-12-21 01:01:43.250286
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f07b24d651cc'
down_revision: Union[str, Sequence[str], None] = '92e9e489bfd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add column allowing NULL temporarily
    op.add_column('users', sa.Column('login_id', sa.String(), nullable=True))

    # 2. Fill with dummy values for existing users
    op.execute("UPDATE users SET login_id = CONCAT('user', id) WHERE login_id IS NULL")

    # 3. Alter column to NOT NULL
    op.alter_column('users', 'login_id', nullable=False)

    # 4. Add new fields
    op.add_column('users', sa.Column('role', sa.String(), server_default='admin', nullable=False))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))

    # 5. Add index
    op.create_index(op.f('ix_users_login_id'), 'users', ['login_id'], unique=True)

    # 6. Drop old admin flag
    op.drop_column('users', 'is_admin')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('users', sa.Column('is_admin', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_users_login_id'), table_name='users')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'role')
    op.drop_column('users', 'login_id')
