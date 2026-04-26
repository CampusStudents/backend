from .base import NotFoundError


class UniversityNotFoundError(NotFoundError):
    message = "University not found"
