"""Add RBAC roles and permissions

Revision ID: 7cbb7a4c2e7a
Revises: 64168f0ebb50
Create Date: 2026-03-27 20:45:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "7cbb7a4c2e7a"
down_revision: Union[str, Sequence[str], None] = "64168f0ebb50"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "permissions",
        sa.Column("subject", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_permissions")),
        sa.UniqueConstraint(
            "subject", "action", name=op.f("uq_permissions_subject_action")
        ),
    )
    op.create_table(
        "roles",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roles")),
        sa.UniqueConstraint("name", name=op.f("uq_roles_name")),
    )
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.Column("permission_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            name=op.f("fk_role_permissions_permission_id_permissions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name=op.f("fk_role_permissions_role_id_roles"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "role_id", "permission_id", name=op.f("pk_role_permissions")
        ),
    )
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name=op.f("fk_user_roles_role_id_roles"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_roles_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "role_id", name=op.f("pk_user_roles")),
    )
    op.drop_column("users", "role")
    op.execute("DROP TYPE IF EXISTS userrole")


def downgrade() -> None:
    op.execute("CREATE TYPE userrole AS ENUM ('user', 'organizer', 'admin')")
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("user", "organizer", "admin", name="userrole"),
            nullable=False,
            server_default="user",
        ),
    )
    op.drop_table("user_roles")
    op.drop_table("role_permissions")
    op.drop_table("roles")
    op.drop_table("permissions")
