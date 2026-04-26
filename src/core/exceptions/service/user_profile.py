from .base import NotFoundError


class UserProfileNotFoundError(NotFoundError):
    message = "User profile not found"
