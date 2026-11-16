"""initial auth tables

Revision ID: 0001_initial_auth
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_auth"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    role = sa.Enum("patient", "doctor", "admin", name="user_role")
    role.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("role", role, nullable=False, server_default="patient"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
def downgrade():
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    sa.Enum("patient", "doctor", "admin", name="user_role").drop(op.get_bind(), checkfirst=True)
