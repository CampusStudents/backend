from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import UUIDPkMixin, TimestampMixin
from .rbac import user_roles

if TYPE_CHECKING:
    from .profile import UserProfile
    from .rbac import Role


class User(UUIDPkMixin, TimestampMixin, Base):
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str]
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

    roles: Mapped[list["Role"]] = relationship(
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )
