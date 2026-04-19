import uuid
from typing import TYPE_CHECKING

from sqlalchemy import TEXT, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .city import City
    from .university import University
    from .user import User


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

    user: Mapped[User] = relationship(back_populates="profile", lazy="raise")
    city: Mapped[City | None] = relationship(lazy="joined")
    university: Mapped[University | None] = relationship(lazy="raise")
