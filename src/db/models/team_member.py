import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .library import TeamRole
    from .project import Project
    from .user import User


class TeamMember(UUIDPkMixin, TimestampMixin, Base):
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "user_id",
            name="uq_team_members_project_id_user_id",
        ),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    team_role_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("team_roles.id", ondelete="RESTRICT")
    )

    joined_at: Mapped[datetime]

    project: Mapped[Project] = relationship()
    user: Mapped[User] = relationship()
    team_role: Mapped[TeamRole | None] = relationship(lazy="joined")
