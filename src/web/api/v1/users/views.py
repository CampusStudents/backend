from uuid import UUID

from fastapi import APIRouter, Security

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.user.schema import UpdateUserRolesSchema, UserDTO
from src.web.api.dependencies import UserServiceDep, get_current_verified_user

router = APIRouter(prefix=settings.api.v1.users)


@router.put("/{user_id}/roles")
async def update_user_roles(
        user_id: UUID,
        data: UpdateUserRolesSchema,
        service: UserServiceDep,
        _: UserDTO = Security(get_current_verified_user, scopes=[Scope.USERS_UPDATE_ROLES]),
) -> UserDTO:
    """
    Назначение/обновление ролей пользователя.
    """
    return await service.update_roles(user_id, data)
