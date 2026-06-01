from .base import NotFoundError


class EventNotFoundError(NotFoundError):
    message = "Event not found"
