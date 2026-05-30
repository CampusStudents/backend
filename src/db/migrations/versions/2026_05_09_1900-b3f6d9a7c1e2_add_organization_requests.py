"""add organization requests

Revision ID: b3f6d9a7c1e2
Revises: a66f887222cc
Create Date: 2026-05-09 19:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b3f6d9a7c1e2"
down_revision: Union[str, Sequence[str], None] = "a66f887222cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

organization_request_status = sa.Enum(
    "pending",
    "approved",
    "rejected",
    name="organization_request_status",
)


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        op.f("uq_organizations_name"),
        "organizations",
        ["name"],
    )
    op.create_table(
        "organization_requests",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("organization_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            organization_request_status,
            nullable=False,
        ),
        sa.Column("reviewed_by_id", sa.UUID(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("reject_reason", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["reviewed_by_id"],
            ["users.id"],
            name=op.f("fk_organization_requests_reviewed_by_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_organization_requests_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organization_requests")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("organization_requests")
    op.drop_constraint(op.f("uq_organizations_name"), "organizations", type_="unique")
    organization_request_status.drop(op.get_bind(), checkfirst=True)
