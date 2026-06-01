from datetime import datetime
from uuid import UUID

import strawberry
from strawberry.types import Info

from src.core.security.scopes import Scope
from src.service.skill.schema import (
    CreateSkillSchema,
    SkillDTO,
    SkillFilter,
    UpdateSkillSchema,
)
from src.web.graphql.permissions import get_context, require_scope


@strawberry.type
class SkillType:
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_dto(cls, dto: SkillDTO) -> "SkillType":
        return cls(
            id=dto.id,
            name=dto.name,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )


@strawberry.input
class SkillFilterInput:
    name: str | None = None
    name_like: str | None = None
    limit: int | None = None
    offset: int = 0

    def to_schema(self) -> SkillFilter:
        return SkillFilter(
            name=self.name,
            name__like=self.name_like,
            limit=self.limit,
            offset=self.offset,
        )


@strawberry.input
class CreateSkillInput:
    name: str

    def to_schema(self) -> CreateSkillSchema:
        return CreateSkillSchema(name=self.name)


@strawberry.input
class UpdateSkillInput:
    name: str | None = None

    def to_schema(self) -> UpdateSkillSchema:
        return UpdateSkillSchema(name=self.name)


async def get_skills(
    info: Info,
    filters: SkillFilterInput | None = None,
) -> list[SkillType]:
    require_scope(info, Scope.SKILLS_LIST)
    service = get_context(info).skill_service
    skill_filter = filters.to_schema() if filters else SkillFilter()
    skills = await service.get_all(skill_filter)
    return [SkillType.from_dto(skill) for skill in skills]


async def get_skill(info: Info, skill_id: UUID) -> SkillType:
    require_scope(info, Scope.SKILLS_DETAIL)
    service = get_context(info).skill_service
    skill = await service.get_by_id(skill_id)
    return SkillType.from_dto(skill)


async def create_skill(info: Info, data: CreateSkillInput) -> SkillType:
    require_scope(info, Scope.SKILLS_CREATE)
    service = get_context(info).skill_service
    skill = await service.create(data.to_schema())
    return SkillType.from_dto(skill)


async def update_skill(
    info: Info,
    skill_id: UUID,
    data: UpdateSkillInput,
) -> SkillType:
    require_scope(info, Scope.SKILLS_UPDATE)
    service = get_context(info).skill_service
    skill = await service.update(skill_id, data.to_schema())
    return SkillType.from_dto(skill)


async def delete_skill(info: Info, skill_id: UUID) -> bool:
    require_scope(info, Scope.SKILLS_DELETE)
    service = get_context(info).skill_service
    await service.delete(skill_id)
    return True
