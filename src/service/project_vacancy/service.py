from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.service.base import NoAccessError
from src.core.exceptions.service.project import ProjectNotFoundError
from src.core.exceptions.service.project_vacancy import ProjectVacancyNotFoundError
from src.core.exceptions.service.skill import SkillNotFoundError
from src.core.exceptions.service.team_role import TeamRoleNotFoundError
from src.db.repository.project import ProjectRepository
from src.db.repository.project_vacancy import ProjectVacancyRepository
from src.db.repository.skill import SkillRepository
from src.db.repository.team_role import TeamRoleRepository
from src.db.unit_of_work import UnitOfWork
from src.service.user.schema import UserDTO

from .schema import (
    CreateProjectVacancySchema,
    ProjectVacancyDTO,
    ProjectVacancyFilter,
    UpdateProjectVacancySchema,
)


class ProjectVacancyService:
    def __init__(
        self,
        uow: UnitOfWork,
        repository: ProjectVacancyRepository,
        project_repository: ProjectRepository,
        team_role_repository: TeamRoleRepository,
        skill_repository: SkillRepository,
    ):
        self.uow = uow
        self.repository = repository
        self.project_repository = project_repository
        self.team_role_repository = team_role_repository
        self.skill_repository = skill_repository

    async def get_by_project_id(
        self,
        project_id: UUID,
        filters: ProjectVacancyFilter,
    ) -> list[ProjectVacancyDTO]:
        async with self.uow as uow:
            await self._ensure_project_exists(uow.session, project_id)
            repository_filters = filters.to_repository_filters()
            repository_filters["project_id"] = project_id
            vacancies = await self.repository.get_multi_out(
                uow.session,
                repository_filters,
            )
            return [ProjectVacancyDTO.model_validate(vacancy) for vacancy in vacancies]

    async def get_by_id(
        self,
        project_id: UUID,
        vacancy_id: UUID,
    ) -> ProjectVacancyDTO:
        async with self.uow as uow:
            vacancy = await self._get_project_vacancy_or_raise(
                uow.session,
                project_id,
                vacancy_id,
            )
            return ProjectVacancyDTO.model_validate(vacancy)

    async def create(
        self,
        project_id: UUID,
        data: CreateProjectVacancySchema,
        user: UserDTO,
    ) -> ProjectVacancyDTO:
        async with self.uow as uow:
            # Validate
            project = await self._ensure_project_exists(uow.session, project_id)
            self._ensure_owner_or_admin(project.owner_id, user)
            await self._ensure_team_role_exists(uow.session, data.team_role_id)
            await self._ensure_skills_exist(uow.session, data.skill_ids)

            # Create
            data_to_create = data.model_dump(exclude={"skill_ids"})
            data_to_create["project_id"] = project_id
            vacancy = await self.repository.create(
                uow.session,
                data_to_create
            )
            await self.repository.set_skills(uow.session, vacancy.id, data.skill_ids)
            await uow.commit()

            created_vacancy = await self._get_by_id_or_raise(uow.session, vacancy.id)
            return ProjectVacancyDTO.model_validate(created_vacancy)

    async def update(
        self,
        project_id: UUID,
        vacancy_id: UUID,
        data: UpdateProjectVacancySchema,
        user: UserDTO,
    ) -> ProjectVacancyDTO:
        async with self.uow as uow:
            project = await self._ensure_project_exists(uow.session, project_id)
            self._ensure_owner_or_admin(project.owner_id, user)
            vacancy = await self._get_project_vacancy_or_raise(
                uow.session,
                project_id,
                vacancy_id,
            )

            data_to_update = data.model_dump(exclude_unset=True)
            skill_ids = data_to_update.pop("skill_ids", None)
            if "team_role_id" in data_to_update:
                await self._ensure_team_role_exists(
                    uow.session, data_to_update["team_role_id"]
                )
            if skill_ids is not None:
                await self._ensure_skills_exist(uow.session, skill_ids)
                await self.repository.set_skills(uow.session, vacancy_id, skill_ids)

            await self.repository.update(uow.session, vacancy_id, data_to_update)
            await uow.commit()

            updated_vacancy = await self._get_by_id_or_raise(uow.session, vacancy.id)
            return ProjectVacancyDTO.model_validate(updated_vacancy)

    async def delete(
        self,
        project_id: UUID,
        vacancy_id: UUID,
        user: UserDTO,
    ) -> None:
        async with self.uow as uow:
            project = await self._ensure_project_exists(uow.session, project_id)
            vacancy = await self._get_project_vacancy_or_raise(uow.session, project_id, vacancy_id)
            self._ensure_owner_or_admin(project.owner_id, user)
            await self.repository.delete_by_id(uow.session, vacancy.id)
            await uow.commit()

    async def _ensure_project_exists(self, session: AsyncSession, project_id: UUID):
        project = await self.project_repository.get(session, {"id": project_id})
        if not project:
            raise ProjectNotFoundError()
        return project

    async def _get_by_id_or_raise(self, session: AsyncSession, vacancy_id: UUID):
        vacancy = await self.repository.get_out(session, {"id": vacancy_id})
        if not vacancy:
            raise ProjectVacancyNotFoundError()
        return vacancy

    async def _get_project_vacancy_or_raise(
        self,
        session: AsyncSession,
        project_id: UUID,
        vacancy_id: UUID,
    ):
        vacancy = await self._get_by_id_or_raise(session, vacancy_id)
        if vacancy.project_id != project_id:
            raise ProjectVacancyNotFoundError()
        return vacancy

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

    def _ensure_owner_or_admin(
        self,
        owner_id: UUID,
        user: UserDTO,
    ) -> None:
        if "*" in user.scopes or owner_id == user.id:
            return
        raise NoAccessError()
