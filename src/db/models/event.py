import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .organization import Organization


class Event(UUIDPkMixin, TimestampMixin, Base):
    organizer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE")
    )

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    date_start: Mapped[datetime]
    date_end: Mapped[datetime]
    application_deadline: Mapped[datetime | None]

    format: Mapped[str | None]
    city: Mapped[str | None]
    registration_link: Mapped[str | None]

    status: Mapped[str]

    organizer: Mapped[Organization] = relationship(lazy="raise")
