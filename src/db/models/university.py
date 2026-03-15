import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import UUIDPkMixin, TimestampMixin

if TYPE_CHECKING:
    from .city import City


class University(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "universities"
    name: Mapped[str]
    short_name: Mapped[str]
    city_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("cities.id", ondelete="SET NULL"))
    city: Mapped["City"] = relationship(lazy="joined")
