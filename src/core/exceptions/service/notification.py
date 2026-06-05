from .base import NotFoundError


class NotificationNotFoundError(NotFoundError):
    message = "Notification not found"
