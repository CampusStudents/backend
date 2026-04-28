from .base import NotFoundError


class ProjectNotFoundError(NotFoundError):
    message = "Project not found"
