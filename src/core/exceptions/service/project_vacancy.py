from .base import NotFoundError


class ProjectVacancyNotFoundError(NotFoundError):
    message = "Project vacancy not found"
