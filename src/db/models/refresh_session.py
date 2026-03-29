import uuid
from datetime import datetime, tzinfo

from sqlalchemy import Text, ForeignKey, DATETIME
from sqlalchemy.orm import mapped_column, Mapped

from src.db.models.mixins import UUIDPkMixin, TimestampMixin
from .base import Base


class RefreshSession(UUIDPkMixin, TimestampMixin, Base):
    refresh_jti: Mapped[str] = mapped_column(Text, unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    expires_at: Mapped[datetime]
