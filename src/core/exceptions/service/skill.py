from .base import NotFoundError


class SkillNotFoundError(NotFoundError):
    message = "Skill not found"
