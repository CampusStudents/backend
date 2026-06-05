from sqlalchemy import Select

from src.db.models import Notification
from src.db.repository.base import SQLAlchemyRepository


class NotificationRepository(SQLAlchemyRepository):
    model = Notification

    def apply_related_load(
        self,
        query: Select[tuple[Notification]],
    ) -> Select[tuple[Notification]]:
        return query
