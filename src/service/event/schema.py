from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
)

from src.db.choices import EventFormat, EventStatus
from src.service.filters import BaseFilter
from src.service.helpers import EntityDTO, NonEmptyStr

InitialEventStatus = Literal[
    EventStatus.DRAFT,
    EventStatus.PUBLISHED,
    EventStatus.REGISTRATION_OPEN,
]


def normalize_datetime_to_utc_naive(value: datetime | None) -> datetime | None:
    if value is None or value.tzinfo is None:
        return value
    return value.astimezone(UTC).replace(tzinfo=None)


class EventBaseSchema(BaseModel):
    organizer_id: UUID | None = None
    city_id: UUID | None = None
    title: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
    ]
    description: str | None = None
    date_start: datetime
    date_end: datetime
    application_deadline: datetime | None = None
    format: EventFormat | None = None
    registration_link: NonEmptyStr | None = None
    status: EventStatus = EventStatus.DRAFT

    _normalize_datetimes = field_validator(
        "date_start",
        "date_end",
        "application_deadline",
    )(normalize_datetime_to_utc_naive)


class CreateEventSchema(EventBaseSchema):
    organizer_id: UUID
    status: InitialEventStatus = EventStatus.DRAFT


class UpdateEventSchema(BaseModel):
    organizer_id: UUID | None = None
    city_id: UUID | None = None
    title: (
        Annotated[
            str,
            StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
        ]
        | None
    ) = None
    description: NonEmptyStr | None = None
    date_start: datetime | None = None
    date_end: datetime | None = None
    application_deadline: datetime | None = None
    format: EventFormat | None = None
    registration_link: str | None = None
    status: EventStatus | None = None

    _normalize_datetimes = field_validator(
        "date_start",
        "date_end",
        "application_deadline",
    )(normalize_datetime_to_utc_naive)


class EventFilter(BaseFilter):
    status__in: list[EventStatus] | None = Field(default=None, alias="status")
    format__in: list[EventFormat] | None = Field(default=None, alias="format")
    city_id__in: list[UUID] | None = Field(default=None, alias="city_id")
    organizer_id__in: list[UUID] | None = Field(default=None, alias="organizer_id")


class EventOrganizerDTO(BaseModel):
    id: UUID
    name: str
    contact_email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class EventImageUrlDTO(EntityDTO):
    event_id: UUID
    url: str


class EventDTO(EventBaseSchema, EntityDTO):
    organizer: EventOrganizerDTO | None = None
    images: list[EventImageUrlDTO] = Field(default_factory=list)


class EventShortDTO(EventBaseSchema, EntityDTO):
    pass
