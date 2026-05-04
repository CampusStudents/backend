from .base import AlreadyExistsError, BadRequestError, NotFoundError


class ApplicationNotFoundError(NotFoundError):
    message = "Application not found"


class ApplicationAlreadyExistsError(AlreadyExistsError):
    message = "Application already exists for this vacancy"


class ProjectOwnerApplicationError(BadRequestError):
    message = "Project owner cannot apply to own vacancy"


class ProjectNotAcceptingApplicationsError(BadRequestError):
    message = "Project is not accepting applications"


class ApplicationStatusTransitionError(BadRequestError):
    message = "Application status transition is not allowed"
