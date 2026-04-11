import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .city import City
    from .event import Event
    from .user import User


class Project(UUIDPkMixin, TimestampMixin, Base):
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL")
    )

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    type: Mapped[str | None]
    format: Mapped[str | None]
    city: Mapped[City] = relationship(lazy="joined")

    deadline: Mapped[datetime | None]
    status: Mapped[str]

    owner: Mapped[User] = relationship(lazy="raise")
    event: Mapped[Event] = relationship(lazy="joined")
