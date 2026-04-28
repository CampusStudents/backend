from uuid import UUID

from fastapi import APIRouter, Security, status

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.user.schema import UserDTO
from src.service.user_profile.schema import (
    CreateUserProfileSchema,
    UpdateUserProfileSchema,
    UserProfileDTO,
)
from src.web.api.dependencies import (
    UserProfileServiceDep,
    get_current_verified_user,
)

router = APIRouter(prefix=settings.api.v1.users)


@router.get("/profile")
async def get_my_profile(
    service: UserProfileServiceDep,
    current_user: UserDTO = Security(
        get_current_verified_user,
        scopes=[Scope.USER_PROFILES_DETAIL],
    ),
) -> UserProfileDTO:
    return await service.get_current_user_profile(current_user.id)


@router.post("/profile", status_code=status.HTTP_201_CREATED)
async def create_my_profile(
    data: CreateUserProfileSchema,
    service: UserProfileServiceDep,
    current_user: UserDTO = Security(
        get_current_verified_user,
        scopes=[Scope.USER_PROFILES_CREATE],
    ),
) -> UserProfileDTO:
    return await service.create(current_user.id, data)


@router.patch("/profile")
async def update_my_profile(
    data: UpdateUserProfileSchema,
    service: UserProfileServiceDep,
    current_user: UserDTO = Security(
        get_current_verified_user,
        scopes=[Scope.USER_PROFILES_UPDATE],
    ),
) -> UserProfileDTO:
    return await service.update(current_user.id, data)


@router.get(
    "/{user_id}/profile",
    dependencies=[
        Security(get_current_verified_user, scopes=[Scope.USER_PROFILES_DETAIL_ANY]),
    ],
)
async def get_user_profile(
    user_id: UUID,
    service: UserProfileServiceDep,
) -> UserProfileDTO:
    return await service.get_by_user_id(user_id)
