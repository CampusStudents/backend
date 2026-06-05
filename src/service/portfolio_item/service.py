from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.service.portfolio_item import PortfolioItemNotFoundError
from src.core.exceptions.service.skill import SkillNotFoundError
from src.core.exceptions.service.team_role import TeamRoleNotFoundError
from src.core.exceptions.service.user import UserNotFoundError
from src.db.repository.portfolio_item import PortfolioItemRepository
from src.db.repository.skill import SkillRepository
from src.db.repository.team_role import TeamRoleRepository
from src.db.repository.user import UserRepository
from src.db.unit_of_work import UnitOfWork
from src.service.skill.schema import SkillDTO

from .schema import (
    CreatePortfolioItemSchema,
    PortfolioItemDTO,
    ReplaceUserSkillsSchema,
    UpdatePortfolioItemSchema,
)


class PortfolioItemService:
    def __init__(
        self,
        uow: UnitOfWork,
        repository: PortfolioItemRepository,
        user_repository: UserRepository,
        team_role_repository: TeamRoleRepository,
        skill_repository: SkillRepository,
    ):
        self.uow = uow
        self.repository = repository
        self.user_repository = user_repository
        self.team_role_repository = team_role_repository
        self.skill_repository = skill_repository

    async def get_current_user_items(self, user_id: UUID) -> list[PortfolioItemDTO]:
        return await self.get_by_user_id(user_id)

    async def get_by_user_id(self, user_id: UUID) -> list[PortfolioItemDTO]:
        async with self.uow as uow:
            await self._ensure_user_exists(uow.session, user_id)
            items = await self.repository.get_multi_out(
                uow.session,
                {"user_id": user_id},
            )
            return [PortfolioItemDTO.model_validate(item) for item in items]

    async def get_current_user_item(
        self,
        user_id: UUID,
        item_id: UUID,
    ) -> PortfolioItemDTO:
        async with self.uow as uow:
            item = await self._get_own_item_or_raise(uow.session, user_id, item_id)
            return PortfolioItemDTO.model_validate(item)

    async def create(
        self,
        user_id: UUID,
        data: CreatePortfolioItemSchema,
    ) -> PortfolioItemDTO:
        async with self.uow as uow:
            await self._ensure_team_role_exists(uow.session, data.team_role_id)
            data_to_create = data.model_dump(mode="json")
            data_to_create["user_id"] = user_id
            item = await self.repository.create(uow.session, data_to_create)
            await uow.commit()

            created_item = await self._get_own_item_or_raise(
                uow.session,
                user_id,
                item.id,
            )
            return PortfolioItemDTO.model_validate(created_item)

    async def update(
        self,
        user_id: UUID,
        item_id: UUID,
        data: UpdatePortfolioItemSchema,
    ) -> PortfolioItemDTO:
        async with self.uow as uow:
            item = await self._get_own_item_or_raise(uow.session, user_id, item_id)
            data_to_update = data.model_dump(mode="json", exclude_unset=True)
            team_role_id = data_to_update.get("team_role_id")
            if team_role_id is not None:
                await self._ensure_team_role_exists(uow.session, team_role_id)

            await self.repository.update(uow.session, item.id, data_to_update)
            await uow.commit()

            updated_item = await self._get_own_item_or_raise(
                uow.session,
                user_id,
                item.id,
            )
            return PortfolioItemDTO.model_validate(updated_item)

    async def delete(self, user_id: UUID, item_id: UUID) -> None:
        async with self.uow as uow:
            item = await self._get_own_item_or_raise(uow.session, user_id, item_id)
            await self.repository.delete_by_id(uow.session, item.id)
            await uow.commit()

    async def get_current_user_skills(self, user_id: UUID) -> list[SkillDTO]:
        return await self.get_user_skills(user_id)

    async def get_user_skills(self, user_id: UUID) -> list[SkillDTO]:
        async with self.uow as uow:
            user = await self._get_user_with_skills_or_raise(uow.session, user_id)
            return [SkillDTO.model_validate(skill) for skill in user.skills]

    async def replace_current_user_skills(
        self,
        user_id: UUID,
        data: ReplaceUserSkillsSchema,
    ) -> list[SkillDTO]:
        async with self.uow as uow:
            await self._ensure_skills_exist(uow.session, data.skill_ids)
            await self.user_repository.replace_skills(
                uow.session,
                user_id,
                data.skill_ids,
            )
            await uow.commit()

            user = await self._get_user_with_skills_or_raise(uow.session, user_id)
            return [SkillDTO.model_validate(skill) for skill in user.skills]

    async def _get_own_item_or_raise(
        self,
        session: AsyncSession,
        user_id: UUID,
        item_id: UUID,
    ):
        item = await self.repository.get_out(
            session,
            {"id": item_id, "user_id": user_id},
        )
        if not item:
            raise PortfolioItemNotFoundError()
        return item

    async def _ensure_user_exists(self, session: AsyncSession, user_id: UUID) -> None:
        user = await self.user_repository.get(session, {"id": user_id})
        if not user:
            raise UserNotFoundError()

    async def _get_user_with_skills_or_raise(
        self,
        session: AsyncSession,
        user_id: UUID,
    ):
        user = await self.user_repository.get_with_skills(session, user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def _ensure_team_role_exists(
        self,
        session: AsyncSession,
        team_role_id: UUID,
    ) -> None:
        team_role = await self.team_role_repository.get(session, {"id": team_role_id})
        if not team_role:
            raise TeamRoleNotFoundError()

    async def _ensure_skills_exist(
        self,
        session: AsyncSession,
        skill_ids: list[UUID],
    ) -> None:
        skills = await self.skill_repository.get_multi(session, {"id__in": skill_ids})
        if len(skills) != len(skill_ids):
            raise SkillNotFoundError()
