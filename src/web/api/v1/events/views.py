from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Query, Security, UploadFile, status

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.event.schema import (
    CreateEventSchema,
    EventDTO,
    EventFilter,
    EventImageUrlDTO,
    UpdateEventSchema,
)
from src.service.user.schema import UserDTO
from src.web.api.dependencies import (
    EventServiceDep,
    get_current_active_user_with_profile,
)

router = APIRouter(prefix=settings.api.v1.events)


@router.get("/")
async def get_events(
    service: EventServiceDep,
    filters: Annotated[EventFilter, Query()],
) -> list[EventDTO]:
    return await service.get_all(filters)


@router.get("/{event_id}")
async def get_event(
    event_id: UUID,
    service: EventServiceDep,
) -> EventDTO:
    return await service.get_by_id(event_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(
    data: CreateEventSchema,
    service: EventServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.EVENTS_CREATE],
    ),
) -> EventDTO:
    return await service.create(data, user)


@router.patch("/{event_id}")
async def update_event(
    event_id: UUID,
    data: UpdateEventSchema,
    service: EventServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.EVENTS_UPDATE],
    ),
) -> EventDTO:
    return await service.update(event_id, data, user)


@router.post("/{event_id}/images", status_code=status.HTTP_201_CREATED)
async def upload_event_image(
    event_id: UUID,
    service: EventServiceDep,
    image: UploadFile = File(...),
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.EVENTS_UPDATE],
    ),
) -> EventImageUrlDTO:
    return await service.upload_image(
        event_id, await image.read(), image.filename, user
    )


@router.delete("/{event_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event_image(
    event_id: UUID,
    image_id: UUID,
    service: EventServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.EVENTS_UPDATE],
    ),
) -> None:
    await service.delete_image(event_id, image_id, user)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: UUID,
    service: EventServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.EVENTS_DELETE],
    ),
) -> None:
    await service.delete(event_id, user)
