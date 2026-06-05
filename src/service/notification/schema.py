from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.db.choices import NotificationType
from src.service.helpers import EntityDTO, NonEmptyStr


class NotificationDTO(EntityDTO):
    user_id: UUID
    application_id: UUID | None = None
    type: NotificationType
    title: NonEmptyStr
    body: NonEmptyStr
    read_at: datetime | None = None


class NotificationFilter(BaseModel):
    unread_only: bool = False
