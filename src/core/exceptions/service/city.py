from .base import NotFoundError


class CityNotFoundError(NotFoundError):
    message = "City not found"
