from datetime import UTC, datetime
from uuid import UUID

from src.core.exceptions.service.notification import NotificationNotFoundError
from src.db.models import Notification
from src.db.repository.notification import NotificationRepository
from src.db.unit_of_work import UnitOfWork
from src.service.user.schema import UserDTO

from .schema import NotificationDTO, NotificationFilter


class NotificationService:
    def __init__(
        self,
        uow: UnitOfWork,
        repository: NotificationRepository,
    ):
        self.uow = uow
        self.repository = repository

    async def get_my_notifications(
        self,
        user: UserDTO,
        filters: NotificationFilter,
    ) -> list[NotificationDTO]:
        async with self.uow as uow:
            query_filters = {"user_id": user.id}
            if filters.unread_only:
                query_filters["read_at"] = None

            notifications = await self.repository.get_multi(
                uow.session,
                query_filters,
                order_by=(Notification.created_at.desc(),),
            )
            return [
                NotificationDTO.model_validate(notification)
                for notification in notifications
            ]

    async def mark_as_read(
        self,
        notification_id: UUID,
        user: UserDTO,
    ) -> NotificationDTO:
        async with self.uow as uow:
            notification = await self.repository.get(
                uow.session,
                {"id": notification_id, "user_id": user.id},
            )
            if not notification:
                raise NotificationNotFoundError()

            updated_notification = await self.repository.update(
                uow.session,
                notification.id,
                {"read_at": datetime.now(UTC).replace(tzinfo=None)},
            )
            await uow.commit()
            return NotificationDTO.model_validate(
                updated_notification or notification,
            )
