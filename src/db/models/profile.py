import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from src.db.models.mixins import UUIDPkMixin, TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .university import University
    from .city import City


class UserProfile(UUIDPkMixin, TimestampMixin, Base):
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(TEXT)
    city_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("cities.id", ondelete="SET NULL")
    )
    university_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("universities.id", ondelete="SET NULL")
    )

    user: Mapped["User"] = relationship(back_populates="profile", lazy="raise")
    city: Mapped["City"] = relationship(lazy="joined")
    university: Mapped["University"] = relationship(lazy="raise")
