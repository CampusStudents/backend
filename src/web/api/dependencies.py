from datetime import datetime, UTC
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.exceptions.service.auth import InvalidTokenError, TokenExpiredError
from src.core.exceptions.service.base import ForbiddenError, NoAccessError
from src.core.security.utils import decode_jwt
from src.db.models.user import UserRole
from src.service.auth.service import AuthService
from src.service.dependencies import get_auth_service, get_user_service
from src.service.user.schema import UserDTO
from src.service.user.service import UserService

http_bearer = HTTPBearer()

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_current_token_payload(
        credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    token = credentials.credentials
    payload = decode_jwt(token)
    exp = payload["exp"]
    if exp < datetime.now(UTC).timestamp():
        raise TokenExpiredError()
    return payload


async def get_token_for_refresh(
        request: Request,
) -> str:
    token = request.cookies.get("refresh_token")
    if token:
        return token
    raise InvalidTokenError("No token")


async def get_current_user(
        service: AuthServiceDep,
        payload: dict = Depends(get_current_token_payload),
) -> UserDTO:
    return await service.get_current_user(payload)


async def get_current_active_user(
        user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    if not user.is_active:
        raise ForbiddenError(
            detail="User inactive",
        )
    return user


async def get_current_verified_user(
        user: UserDTO = Depends(get_current_active_user),
) -> UserDTO:
    if not user.is_verified:
        raise ForbiddenError(
            "Email not verified. Please verify your email address.",
        )
    return user


async def get_current_active_user_with_profile(
        user: UserDTO = Depends(get_current_verified_user),
) -> UserDTO:
    if not user.is_profile_completed:
        raise ForbiddenError(
            "Profile not completed. "
            "Please complete your profile at POST /api/v1/users/profile",
        )
    return user


async def get_current_superuser(
        user: UserDTO = Depends(get_current_active_user_with_profile),
) -> UserDTO:
    if not user.role == UserRole.ADMIN:
        raise NoAccessError()
    return user


CurrentUserDep = Annotated[UserDTO, Depends(get_current_verified_user)]
AdminUserDep = Annotated[UserDTO, Depends(get_current_superuser)]
