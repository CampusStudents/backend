from .base import NotFoundError


class UserNotFoundError(NotFoundError):
    message = "User not found"
