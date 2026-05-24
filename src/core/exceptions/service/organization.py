from .base import AlreadyExistsError, NotFoundError


class OrganizationNotFoundError(NotFoundError):
    message = "Organization not found"


class OrganizationAlreadyExistsError(AlreadyExistsError):
    message = "Organization already exists"
