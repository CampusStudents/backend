import uuid
from datetime import datetime

from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from src.db.models.mixins import UUIDPkMixin, TimestampMixin
from .base import Base


class RefreshSession(UUIDPkMixin, TimestampMixin, Base):
    refresh_token: Mapped[str] = mapped_column(Text, unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    expires_at: Mapped[datetime]
