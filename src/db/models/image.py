import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .event import Event
    from .organization import Organization


class EventImageUrl(UUIDPkMixin, TimestampMixin, Base):
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"),
        index=True,
    )
    url: Mapped[str] = mapped_column(String(2048))

    event: Mapped[Event] = relationship(back_populates="images")


class OrganizationImageUrl(UUIDPkMixin, TimestampMixin, Base):
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
    )
    url: Mapped[str] = mapped_column(String(2048))

    organization: Mapped[Organization] = relationship(back_populates="images")
