from .base import NotFoundError


class TeamRoleNotFoundError(NotFoundError):
    message = "Team role not found"
