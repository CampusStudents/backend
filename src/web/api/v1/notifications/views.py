from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Security

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.notification.schema import NotificationDTO, NotificationFilter
from src.service.user.schema import UserDTO
from src.web.api.dependencies import (
    NotificationServiceDep,
    get_current_active_user,
)

router = APIRouter(prefix=settings.api.v1.notifications)


@router.get("/me")
async def get_my_notifications(
    service: NotificationServiceDep,
    filters: Annotated[NotificationFilter, Query()],
    user: UserDTO = Security(
        get_current_active_user,
        scopes=[Scope.NOTIFICATIONS_LIST],
    ),
) -> list[NotificationDTO]:
    return await service.get_my_notifications(user, filters)


@router.patch("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: UUID,
    service: NotificationServiceDep,
    user: UserDTO = Security(
        get_current_active_user,
        scopes=[Scope.NOTIFICATIONS_UPDATE],
    ),
) -> NotificationDTO:
    return await service.mark_as_read(notification_id, user)
