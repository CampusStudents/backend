from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.service.project import ProjectNotFoundError
from src.db.models import TeamMember
from src.db.repository.project import ProjectRepository
from src.db.repository.team_member import TeamMemberRepository
from src.db.unit_of_work import UnitOfWork

from .schema import TeamMemberDTO


class TeamMemberService:
    def __init__(
        self,
        uow: UnitOfWork,
        repository: TeamMemberRepository,
        project_repository: ProjectRepository,
    ):
        self.uow = uow
        self.repository = repository
        self.project_repository = project_repository

    async def get_by_project(self, project_id: UUID) -> list[TeamMemberDTO]:
        async with self.uow as uow:
            await self._ensure_project_exists(uow.session, project_id)
            team_members = await self.repository.get_multi_out(
                uow.session,
                {"project_id": project_id},
                order_by=(TeamMember.joined_at.asc(),),
            )
            return [
                TeamMemberDTO.model_validate(team_member)
                for team_member in team_members
            ]

    async def _ensure_project_exists(
        self,
        session: AsyncSession,
        project_id: UUID,
    ) -> None:
        project = await self.project_repository.get(session, {"id": project_id})
        if not project:
            raise ProjectNotFoundError()
