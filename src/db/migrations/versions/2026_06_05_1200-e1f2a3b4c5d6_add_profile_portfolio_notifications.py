"""add profile portfolio notifications

Revision ID: e1f2a3b4c5d6
Revises: d4e8c9f0a1b2
Create Date: 2026-06-05 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, Sequence[str], None] = "d4e8c9f0a1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


notification_type = sa.Enum(
    "application_decision",
    name="notification_type",
)


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("user_profiles", sa.Column("status", sa.Text(), nullable=True))
    op.add_column(
        "user_profiles",
        sa.Column("telegram", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("site", sa.String(length=2048), nullable=True),
    )
    op.add_column(
        "portfolio_items",
        sa.Column("work_started_at", sa.Date(), nullable=True),
    )
    op.add_column(
        "portfolio_items",
        sa.Column("work_ended_at", sa.Date(), nullable=True),
    )

    op.create_table(
        "notifications",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("application_id", sa.UUID(), nullable=True),
        sa.Column(
            "type",
            notification_type,
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["applications.id"],
            name=op.f("fk_notifications_application_id_applications"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_notifications_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
    )
    op.create_index(
        op.f("ix_notifications_application_id"),
        "notifications",
        ["application_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_read_at"),
        "notifications",
        ["read_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_user_id"),
        "notifications",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_read_at"), table_name="notifications")
    op.drop_index(
        op.f("ix_notifications_application_id"),
        table_name="notifications",
    )
    op.drop_table("notifications")
    op.drop_column("portfolio_items", "work_ended_at")
    op.drop_column("portfolio_items", "work_started_at")
    op.drop_column("user_profiles", "site")
    op.drop_column("user_profiles", "telegram")
    op.drop_column("user_profiles", "status")
    notification_type.drop(op.get_bind(), checkfirst=True)
