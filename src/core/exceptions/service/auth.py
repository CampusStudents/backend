from .base import AuthError


class InvalidTokenError(AuthError):
    message = "Invalid Token Error"


class NotAuthenticatedError(AuthError):
    message = "Not Authenticated"


class TokenExpiredError(InvalidTokenError):
    message = "Token expired"


class AccountNotVerifiedError(AuthError):
    message = "Account is not verified"
