import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.choices import EventFormat, EventStatus, enum_values

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .library import City
    from .organization import Organization


class Event(UUIDPkMixin, TimestampMixin, Base):
    organizer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL")
    )
    city_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("cities.id", ondelete="RESTRICT")
    )

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    date_start: Mapped[datetime]
    date_end: Mapped[datetime]
    application_deadline: Mapped[datetime | None]

    format: Mapped[EventFormat | None] = mapped_column(
        SQLAlchemyEnum(
            EventFormat,
            name="event_format",
            values_callable=enum_values,
        )
    )
    registration_link: Mapped[str | None]

    status: Mapped[EventStatus] = mapped_column(
        SQLAlchemyEnum(
            EventStatus,
            name="event_status",
            values_callable=enum_values,
        ),
        default=EventStatus.DRAFT,
    )

    city: Mapped[City | None] = relationship(lazy="joined")
    organizer: Mapped[Organization | None] = relationship(back_populates="events")
