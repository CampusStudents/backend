from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes

from src.core.exceptions.service.auth import InvalidTokenError
from src.core.exceptions.service.base import ForbiddenError
from src.core.security.utils import decode_jwt
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
    return payload


async def get_token_for_refresh(
        request: Request,
) -> str:
    token = request.cookies.get("refresh_token")
    if token:
        return token
    raise InvalidTokenError("No token")


async def get_current_user(
        security_scopes: SecurityScopes,
        service: AuthServiceDep,
        payload: dict = Depends(get_current_token_payload),
) -> UserDTO:
    user = await service.get_current_user(payload)
    user_scopes = user.scopes
    for scope in security_scopes.scopes:
        if scope not in user_scopes and "*" not in user_scopes:
            raise ForbiddenError("Insufficient permissions")
    return user


async def get_current_active_user(
        security_scopes: SecurityScopes,
        service: AuthServiceDep,
        payload: dict = Depends(get_current_token_payload),
) -> UserDTO:
    user = await get_current_user(security_scopes, service, payload)
    if not user.is_active:
        raise ForbiddenError(
            detail="User inactive",
        )
    return user


async def get_current_verified_user(
        security_scopes: SecurityScopes,
        service: AuthServiceDep,
        payload: dict = Depends(get_current_token_payload),
) -> UserDTO:
    user = await get_current_active_user(security_scopes, service, payload)
    if not user.is_verified:
        raise ForbiddenError(
            "Email not verified. Please verify your email address.",
        )
    return user


async def get_current_active_user_with_profile(
        security_scopes: SecurityScopes,
        service: AuthServiceDep,
        payload: dict = Depends(get_current_token_payload),
) -> UserDTO:
    user = await get_current_verified_user(security_scopes, service, payload)
    if not user.is_profile_completed:
        raise ForbiddenError(
            "Profile not completed. "
            "Please complete your profile at POST /api/v1/users/profile",
        )
    return user

