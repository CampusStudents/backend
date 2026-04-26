from enum import StrEnum


class EventFormat(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"


class EventStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
