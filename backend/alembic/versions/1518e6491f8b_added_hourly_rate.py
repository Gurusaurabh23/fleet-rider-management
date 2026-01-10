from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1518e6491f8b'
down_revision = 'cf1088ba97d3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('hourly_rate', sa.Float(), nullable=True))


def downgrade():
    op.drop_column('users', 'hourly_rate')
