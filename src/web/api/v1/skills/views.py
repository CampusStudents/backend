from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Security, status

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.skill.schema import (
    CreateSkillSchema,
    SkillDTO,
    SkillFilter,
    UpdateSkillSchema,
)
from src.web.api.dependencies import SkillServiceDep, get_current_active_user

router = APIRouter(prefix=settings.api.v1.skills)


@router.get(
    "/",
    dependencies=[Security(get_current_active_user, scopes=[Scope.SKILLS_LIST])],
)
async def get_skills(
    service: SkillServiceDep,
    filters: Annotated[SkillFilter, Query()],
) -> list[SkillDTO]:
    return await service.get_all(filters)


@router.get(
    "/{skill_id}",
    dependencies=[Security(get_current_active_user, scopes=[Scope.SKILLS_DETAIL])],
)
async def get_skill(
    skill_id: UUID,
    service: SkillServiceDep,
) -> SkillDTO:
    return await service.get_by_id(skill_id)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(get_current_active_user, scopes=[Scope.SKILLS_CREATE])],
)
async def create_skill(
    data: CreateSkillSchema,
    service: SkillServiceDep,
) -> SkillDTO:
    return await service.create(data)


@router.patch(
    "/{skill_id}",
    dependencies=[Security(get_current_active_user, scopes=[Scope.SKILLS_UPDATE])],
)
async def update_skill(
    skill_id: UUID,
    data: UpdateSkillSchema,
    service: SkillServiceDep,
) -> SkillDTO:
    return await service.update(skill_id, data)


@router.delete(
    "/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Security(get_current_active_user, scopes=[Scope.SKILLS_DELETE])],
)
async def delete_skill(
    skill_id: UUID,
    service: SkillServiceDep,
) -> None:
    await service.delete(skill_id)
