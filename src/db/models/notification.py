import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.choices import NotificationType, enum_values

from .base import Base
from .mixins import TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from .application import Application
    from .user import User


class Notification(UUIDPkMixin, TimestampMixin, Base):
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("applications.id", ondelete="SET NULL"),
    )
    type: Mapped[NotificationType] = mapped_column(
        SQLAlchemyEnum(
            NotificationType,
            name="notification_type",
            values_callable=enum_values,
        ),
    )
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    read_at: Mapped[datetime | None]

    user: Mapped[User] = relationship(back_populates="notifications")
    application: Mapped[Application | None] = relationship()
