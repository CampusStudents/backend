from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.service.base import AlreadyExistsError
from src.core.exceptions.service.skill import SkillNotFoundError
from src.db.repository.skill import SkillRepository
from src.db.unit_of_work import UnitOfWork

from .schema import CreateSkillSchema, SkillDTO, SkillFilter, UpdateSkillSchema


class SkillService:
    def __init__(self, uow: UnitOfWork, repository: SkillRepository):
        self.uow = uow
        self.repository = repository

    async def get_all(self, filters: SkillFilter) -> list[SkillDTO]:
        async with self.uow as uow:
            skills = await self.repository.get_multi(
                uow.session,
                filters.to_repository_filters(),
            )
            return [SkillDTO.model_validate(skill) for skill in skills]

    async def get_by_id(self, skill_id: UUID) -> SkillDTO:
        async with self.uow as uow:
            skill = await self._get_by_id_or_raise(uow.session, skill_id)
            return SkillDTO.model_validate(skill)

    async def create(self, data: CreateSkillSchema) -> SkillDTO:
        async with self.uow as uow:
            await self._ensure_name_is_unique(uow.session, data.name)
            skill = await self.repository.create(uow.session, {"name": data.name})
            await uow.commit()
            return SkillDTO.model_validate(skill)

    async def update(self, skill_id: UUID, data: UpdateSkillSchema) -> SkillDTO:
        async with self.uow as uow:
            skill = await self._get_by_id_or_raise(uow.session, skill_id)
            data_to_update = data.model_dump(exclude_unset=True)
            if "name" in data_to_update and skill.name != data_to_update["name"]:
                await self._ensure_name_is_unique(uow.session, data_to_update["name"])

            updated_skill = await self.repository.update(
                uow.session,
                skill_id,
                data_to_update,
            )
            await uow.commit()
            return SkillDTO.model_validate(updated_skill or skill)

    async def delete(self, skill_id: UUID) -> None:
        async with self.uow as uow:
            await self._get_by_id_or_raise(uow.session, skill_id)
            await self.repository.delete_by_id(uow.session, skill_id)
            await uow.commit()

    async def _get_by_id_or_raise(self, session: AsyncSession, skill_id: UUID):
        skill = await self.repository.get(session, {"id": skill_id})
        if not skill:
            raise SkillNotFoundError()
        return skill

    async def _ensure_name_is_unique(self, session: AsyncSession, name: str) -> None:
        existing_skill = await self.repository.get_out(session, {"name": name})
        if existing_skill:
            msg = "Skill already exists"
            raise AlreadyExistsError(msg)
