from alembic import op
import sqlalchemy as sa

revision = "xxxxx"
down_revision = "f07b24d651cc"  # your latest successful
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "red_zones",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("radius_m", sa.Integer, nullable=False, server_default="300"), # default radius 300m
        sa.Column("bonus_pct", sa.Float, nullable=False, server_default="5.0"),  # 5% bonus
        sa.Column("active", sa.Boolean, nullable=False, server_default="true")
    )

def downgrade():
    op.drop_table("red_zones")
