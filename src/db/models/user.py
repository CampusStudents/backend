from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import UUIDPkMixin, TimestampMixin

if TYPE_CHECKING:
    from .profile import UserProfile


class UserRole(str, Enum):
    USER = "user"
    ORGANIZER = "organizer"
    ADMIN = "admin"


class User(UUIDPkMixin, TimestampMixin, Base):
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str]
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    token_version: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_profile_completed: Mapped[bool] = mapped_column(default=False)
    last_login_at: Mapped[datetime | None]

    profile: Mapped["UserProfile"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )
