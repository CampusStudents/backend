import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .project import Project
    from .rbac import Role
    from .user import User


class TeamMember(UUIDPkMixin, TimestampMixin, Base):
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("roles.id", ondelete="SET NULL")
    )

    joined_at: Mapped[datetime]

    project: Mapped["Project"] = relationship(lazy="raise")
    user: Mapped["User"] = relationship(lazy="raise")
    role: Mapped["Role | None"] = relationship(lazy="joined")
