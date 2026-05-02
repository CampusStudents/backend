from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Security, status

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.team_role.schema import (
    CreateTeamRoleSchema,
    TeamRoleDTO,
    TeamRoleFilter,
    UpdateTeamRoleSchema,
)
from src.web.api.dependencies import TeamRoleServiceDep, get_current_active_user

router = APIRouter(prefix=settings.api.v1.team_roles)


@router.get("/")
async def get_team_roles(
    service: TeamRoleServiceDep,
    filters: Annotated[TeamRoleFilter, Query()],
) -> list[TeamRoleDTO]:
    return await service.get_all(filters)


@router.get("/{team_role_id}")
async def get_team_role(
    team_role_id: UUID,
    service: TeamRoleServiceDep,
) -> TeamRoleDTO:
    return await service.get_by_id(team_role_id)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.TEAM_ROLES_CREATE]),
    ],
)
async def create_team_role(
    data: CreateTeamRoleSchema,
    service: TeamRoleServiceDep,
) -> TeamRoleDTO:
    return await service.create(data)


@router.patch(
    "/{team_role_id}",
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.TEAM_ROLES_UPDATE]),
    ],
)
async def update_team_role(
    team_role_id: UUID,
    data: UpdateTeamRoleSchema,
    service: TeamRoleServiceDep,
) -> TeamRoleDTO:
    return await service.update(team_role_id, data)


@router.delete(
    "/{team_role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.TEAM_ROLES_DELETE]),
    ],
)
async def delete_team_role(
    team_role_id: UUID,
    service: TeamRoleServiceDep,
) -> None:
    await service.delete(team_role_id)
