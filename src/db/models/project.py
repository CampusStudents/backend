import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.choices import ProjectFormat, ProjectStatus, ProjectType, enum_values

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .event import Event
    from .library import City
    from .project_vacancy import ProjectVacancy
    from .user import User


class Project(UUIDPkMixin, TimestampMixin, Base):
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL")
    )
    city_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("cities.id", ondelete="RESTRICT")
    )

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    type: Mapped[ProjectType] = mapped_column(
        SQLAlchemyEnum(
            ProjectType,
            name="project_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )
    format: Mapped[ProjectFormat] = mapped_column(
        SQLAlchemyEnum(
            ProjectFormat,
            name="project_format",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    deadline: Mapped[datetime | None]
    status: Mapped[ProjectStatus] = mapped_column(
        SQLAlchemyEnum(
            ProjectStatus,
            name="project_status",
            values_callable=enum_values,
        ),
        default=ProjectStatus.NEW,
    )

    owner: Mapped[User | None] = relationship()
    event: Mapped[Event | None] = relationship()
    city: Mapped[City | None] = relationship(lazy="joined")
    vacancies: Mapped[list[ProjectVacancy]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
