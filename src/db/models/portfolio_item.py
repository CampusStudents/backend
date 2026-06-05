import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .library import TeamRole
    from .user import User


class PortfolioItem(UUIDPkMixin, TimestampMixin, Base):
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    work_started_at: Mapped[date | None]
    work_ended_at: Mapped[date | None]
    team_role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("team_roles.id", ondelete="RESTRICT")
    )
    project_link: Mapped[str | None]

    user: Mapped[User] = relationship()
    team_role: Mapped[TeamRole] = relationship(lazy="joined")
