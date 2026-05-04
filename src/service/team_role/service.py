from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.service.base import AlreadyExistsError
from src.core.exceptions.service.team_role import TeamRoleNotFoundError
from src.db.repository.team_role import TeamRoleRepository
from src.db.unit_of_work import UnitOfWork

from .schema import (
    CreateTeamRoleSchema,
    TeamRoleDTO,
    TeamRoleFilter,
    UpdateTeamRoleSchema,
)


class TeamRoleService:
    def __init__(self, uow: UnitOfWork, repository: TeamRoleRepository):
        self.uow = uow
        self.repository = repository

    async def get_all(self, filters: TeamRoleFilter) -> list[TeamRoleDTO]:
        async with self.uow as uow:
            team_roles = await self.repository.get_multi(
                uow.session,
                filters.to_repository_filters(),
            )
            return [TeamRoleDTO.model_validate(team_role) for team_role in team_roles]

    async def get_by_id(self, team_role_id: UUID) -> TeamRoleDTO:
        async with self.uow as uow:
            team_role = await self._get_by_id_or_raise(uow.session, team_role_id)
            return TeamRoleDTO.model_validate(team_role)

    async def create(self, data: CreateTeamRoleSchema) -> TeamRoleDTO:
        async with self.uow as uow:
            await self._ensure_name_is_unique(uow.session, data.name)
            team_role = await self.repository.create(uow.session, data.model_dump())
            await uow.commit()
            return TeamRoleDTO.model_validate(team_role)

    async def update(
        self,
        team_role_id: UUID,
        data: UpdateTeamRoleSchema,
    ) -> TeamRoleDTO:
        async with self.uow as uow:
            team_role = await self._get_by_id_or_raise(uow.session, team_role_id)
            data_to_update = data.model_dump(exclude_unset=True)
            if "name" in data_to_update and team_role.name != data_to_update["name"]:
                await self._ensure_name_is_unique(uow.session, data_to_update["name"])

            updated_team_role = await self.repository.update(
                uow.session,
                team_role_id,
                data_to_update,
            )
            await uow.commit()
            return TeamRoleDTO.model_validate(updated_team_role or team_role)

    async def delete(self, team_role_id: UUID) -> None:
        async with self.uow as uow:
            await self._get_by_id_or_raise(uow.session, team_role_id)
            await self.repository.delete_by_id(uow.session, team_role_id)
            await uow.commit()

    async def _get_by_id_or_raise(
        self,
        session: AsyncSession,
        team_role_id: UUID,
    ):
        team_role = await self.repository.get(session, {"id": team_role_id})
        if not team_role:
            raise TeamRoleNotFoundError()
        return team_role

    async def _ensure_name_is_unique(self, session: AsyncSession, name: str) -> None:
        existing_team_role = await self.repository.get_out(session, {"name": name})
        if existing_team_role:
            msg = "Team role already exists"
            raise AlreadyExistsError(msg)
