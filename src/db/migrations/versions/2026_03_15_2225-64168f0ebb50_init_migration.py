"""Init migration

Revision ID: 64168f0ebb50
Revises:
Create Date: 2026-03-15 22:25:00.626487

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "64168f0ebb50"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "cities",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cities")),
        sa.UniqueConstraint("name", name=op.f("uq_cities_name")),
    )
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("user", "organizer", "admin", name="userrole"),
            nullable=False,
        ),
        sa.Column("token_version", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_profile_completed", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_table(
        "refresh_sessions",
        sa.Column("refresh_jti", sa.Text(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_refresh_sessions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refresh_sessions")),
        sa.UniqueConstraint(
            "refresh_jti", name=op.f("uq_refresh_sessions_refresh_jti")
        ),
    )
    op.create_table(
        "universities",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("short_name", sa.String(), nullable=False),
        sa.Column("city_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["city_id"],
            ["cities.id"],
            name=op.f("fk_universities_city_id_cities"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_universities")),
    )
    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("bio", sa.TEXT(), nullable=True),
        sa.Column("city_id", sa.UUID(), nullable=True),
        sa.Column("university_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["city_id"],
            ["cities.id"],
            name=op.f("fk_user_profiles_city_id_cities"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["university_id"],
            ["universities.id"],
            name=op.f("fk_user_profiles_university_id_universities"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_profiles_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_profiles")),
        sa.UniqueConstraint("user_id", name=op.f("uq_user_profiles_user_id")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_profiles")
    op.drop_table("universities")
    op.drop_table("refresh_sessions")
    op.drop_table("users")
    op.drop_table("cities")
