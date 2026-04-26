from .base import NotFoundError


class RoleNotFoundError(NotFoundError):
    message = "Role not found"
