from .base import BadRequestError, NotFoundError


class OrganizationRequestNotFoundError(NotFoundError):
    message = "Organization request not found"


class OrganizationRequestStatusError(BadRequestError):
    message = "Organization request status transition is not allowed"
