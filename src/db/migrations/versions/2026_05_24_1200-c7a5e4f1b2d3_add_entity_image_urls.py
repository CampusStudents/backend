"""add entity image urls

Revision ID: c7a5e4f1b2d3
Revises: b3f6d9a7c1e2
Create Date: 2026-05-24 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c7a5e4f1b2d3"
down_revision: Union[str, Sequence[str], None] = "b3f6d9a7c1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "event_image_urls",
        sa.Column("event_id", sa.UUID(), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
            name=op.f("fk_event_image_urls_event_id_events"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_event_image_urls")),
    )
    op.create_index(
        op.f("ix_event_image_urls_event_id"),
        "event_image_urls",
        ["event_id"],
        unique=False,
    )
    op.create_table(
        "organization_image_urls",
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_organization_image_urls_organization_id_organizations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organization_image_urls")),
    )
    op.create_index(
        op.f("ix_organization_image_urls_organization_id"),
        "organization_image_urls",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_organization_image_urls_organization_id"),
        table_name="organization_image_urls",
    )
    op.drop_table("organization_image_urls")
    op.drop_index(op.f("ix_event_image_urls_event_id"), table_name="event_image_urls")
    op.drop_table("event_image_urls")
