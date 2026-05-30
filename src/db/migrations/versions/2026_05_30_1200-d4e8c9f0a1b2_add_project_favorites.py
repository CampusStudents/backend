"""add project favorites

Revision ID: d4e8c9f0a1b2
Revises: c7a5e4f1b2d3
Create Date: 2026-05-30 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4e8c9f0a1b2"
down_revision: Union[str, Sequence[str], None] = "c7a5e4f1b2d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "project_favorites",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_project_favorites_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_project_favorites_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "user_id",
            "project_id",
            name=op.f("pk_project_favorites"),
        ),
    )
    op.create_index(
        op.f("ix_project_favorites_project_id"),
        "project_favorites",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_favorites_user_id"),
        "project_favorites",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_project_favorites_user_id"),
        table_name="project_favorites",
    )
    op.drop_index(
        op.f("ix_project_favorites_project_id"),
        table_name="project_favorites",
    )
    op.drop_table("project_favorites")
