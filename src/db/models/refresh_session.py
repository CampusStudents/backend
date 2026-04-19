import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.mixins import TimestampMixin, UUIDPkMixin

from .base import Base


class RefreshSession(UUIDPkMixin, TimestampMixin, Base):
    refresh_jti: Mapped[str] = mapped_column(Text, unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    expires_at: Mapped[datetime]
