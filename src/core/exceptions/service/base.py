class AppError(Exception):
    message = "Application error"

    def __init__(self, detail: str | None = None):
        super().__init__(detail or self.message)
        self.detail = detail or self.message


class NotFoundError(AppError):
    message = "Resource not found"


class ConflictError(AppError):
    message = "Conflict"


class AlreadyExistsError(ConflictError):
    message = "Resource already exists"


class InvalidInputError(AppError):
    message = "Invalid input"


class ForbiddenError(AppError):
    message = "Forbidden"


class NoAccessError(ForbiddenError):
    message = "You do not have access to this resource"


class BadRequestError(AppError):
    message = "Bad Request"

class AuthError(AppError):
    message = "Auth Error"
