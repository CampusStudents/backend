import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .project import Project
    from .rbac import Role


class ProjectVacancy(UUIDPkMixin, TimestampMixin, Base):
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE")
    )

    required_count: Mapped[int]
    description: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project] = relationship(lazy="raise")
    role: Mapped[Role] = relationship(lazy="joined")
