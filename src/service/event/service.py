from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.service.aws import ImageNotFoundError
from src.core.exceptions.service.base import BadRequestError, NoAccessError
from src.core.exceptions.service.city import CityNotFoundError
from src.core.exceptions.service.event import EventNotFoundError
from src.core.exceptions.service.organization import OrganizationNotFoundError
from src.db.models import Event
from src.db.repository.city import CityRepository
from src.db.repository.event import EventRepository
from src.db.repository.image import EventImageUrlRepository
from src.db.repository.organization import OrganizationRepository
from src.db.unit_of_work import UnitOfWork
from src.service.image_upload.service import ImageUploadService
from src.service.user.schema import UserDTO

from .schema import (
    CreateEventSchema,
    EventDTO,
    EventFilter,
    EventImageUrlDTO,
    UpdateEventSchema,
)


class EventService:
    def __init__(
        self,
        uow: UnitOfWork,
        repository: EventRepository,
        city_repository: CityRepository,
        organization_repository: OrganizationRepository,
        image_repository: EventImageUrlRepository,
    ):
        self.uow = uow
        self.repository = repository
        self.city_repository = city_repository
        self.organization_repository = organization_repository
        self.image_repository = image_repository

    async def get_all(self, filters: EventFilter) -> list[EventDTO]:
        async with self.uow as uow:
            events = await self.repository.get_multi_out(
                uow.session,
                filters.to_repository_filters(),
                order_by=(Event.date_start.asc(),),
            )
            return [EventDTO.model_validate(event) for event in events]

    async def get_by_id(self, event_id: UUID) -> EventDTO:
        async with self.uow as uow:
            event = await self._get_by_id_or_raise(uow.session, event_id)
            return EventDTO.model_validate(event)

    async def create(self, data: CreateEventSchema, user: UserDTO) -> EventDTO:
        async with self.uow as uow:
            await self._ensure_city_exists(uow.session, data.city_id)
            await self._ensure_organization_access(
                uow.session,
                data.organizer_id,
                user,
            )
            self._validate_dates(
                data.date_start,
                data.date_end,
                data.application_deadline,
            )

            event = await self.repository.create(uow.session, data.model_dump())
            await uow.commit()
            created_event = await self._get_by_id_or_raise(uow.session, event.id)
            return EventDTO.model_validate(created_event)

    async def update(
        self,
        event_id: UUID,
        data: UpdateEventSchema,
        user: UserDTO,
    ) -> EventDTO:
        async with self.uow as uow:
            event = await self._get_by_id_or_raise(uow.session, event_id)
            self._ensure_event_owner_or_admin(event, user)

            data_to_update = data.model_dump(exclude_unset=True)
            if not data_to_update:
                msg = "Empty update data"
                raise BadRequestError(msg)

            organizer_id = data_to_update.get("organizer_id", event.organizer_id)
            await self._ensure_organization_access(uow.session, organizer_id, user)
            if data_to_update.get("city_id") is not None:
                await self._ensure_city_exists(uow.session, data_to_update["city_id"])

            date_start = data_to_update.get("date_start", event.date_start)
            date_end = data_to_update.get("date_end", event.date_end)
            application_deadline = data_to_update.get(
                "application_deadline",
                event.application_deadline,
            )
            self._validate_dates(date_start, date_end, application_deadline)

            await self.repository.update(uow.session, event_id, data_to_update)
            await uow.commit()
            updated_event = await self._get_by_id_or_raise(uow.session, event_id)
            return EventDTO.model_validate(updated_event)

    async def delete(self, event_id: UUID, user: UserDTO) -> None:
        async with self.uow as uow:
            event = await self._get_by_id_or_raise(uow.session, event_id)
            self._ensure_event_owner_or_admin(event, user)
            for image in event.images:
                await ImageUploadService.delete_image(image.url)
            await self.repository.delete_by_id(uow.session, event_id)
            await uow.commit()

    async def upload_image(
        self,
        event_id: UUID,
        image_data: bytes,
        file_name: str | None,
        content_type: str | None,
        user: UserDTO,
    ) -> EventImageUrlDTO:
        async with self.uow as uow:
            event = await self._get_by_id_or_raise(uow.session, event_id)
            self._ensure_event_owner_or_admin(event, user)
            image_url = await ImageUploadService.upload_image(
                image_data,
                file_name,
                content_type,
                folder="events",
            )
            try:
                image = await self.image_repository.create(
                    uow.session,
                    {"event_id": event_id, "url": image_url},
                )
                await uow.commit()
                return EventImageUrlDTO.model_validate(image)
            except Exception:
                await ImageUploadService.delete_image(image_url)
                raise

    async def delete_image(
        self,
        event_id: UUID,
        image_id: UUID,
        user: UserDTO,
    ) -> None:
        async with self.uow as uow:
            event = await self._get_by_id_or_raise(uow.session, event_id)
            self._ensure_event_owner_or_admin(event, user)
            image = await self.image_repository.get(
                uow.session,
                {"id": image_id, "event_id": event_id},
            )
            if not image:
                raise ImageNotFoundError()
            await ImageUploadService.delete_image(image.url)
            await self.image_repository.delete_by_id(uow.session, image_id)
            await uow.commit()

    async def _get_by_id_or_raise(self, session: AsyncSession, event_id: UUID):
        event = await self.repository.get_out(session, {"id": event_id})
        if not event:
            raise EventNotFoundError()
        return event

    async def _ensure_city_exists(
        self,
        session: AsyncSession,
        city_id: UUID | None,
    ) -> None:
        if city_id is None:
            return
        city = await self.city_repository.get(session, {"id": city_id})
        if not city:
            raise CityNotFoundError()

    async def _ensure_organization_access(
        self,
        session: AsyncSession,
        organization_id: UUID | None,
        user: UserDTO,
    ) -> None:
        if organization_id is None:
            raise OrganizationNotFoundError()
        organization = await self.organization_repository.get(
            session,
            {"id": organization_id},
        )
        if not organization:
            raise OrganizationNotFoundError()
        if "*" in user.scopes or organization.owner_user_id == user.id:
            return
        raise NoAccessError()

    def _ensure_event_owner_or_admin(self, event: Event, user: UserDTO) -> None:
        if "*" in user.scopes:
            return
        if event.organizer and event.organizer.owner_user_id == user.id:
            return
        raise NoAccessError()

    def _validate_dates(
        self,
        date_start,
        date_end,
        application_deadline,
    ) -> None:
        if date_end < date_start:
            msg = "Event date_end cannot be earlier than date_start"
            raise BadRequestError(msg)
        if application_deadline is not None and application_deadline > date_end:
            msg = "Event application_deadline cannot be later than date_end"
            raise BadRequestError(msg)
