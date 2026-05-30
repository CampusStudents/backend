from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.service.base import BadRequestError, NoAccessError
from src.core.exceptions.service.city import CityNotFoundError
from src.core.exceptions.service.event import EventNotFoundError
from src.core.exceptions.service.project import ProjectNotFoundError
from src.db.choices import ApplicationStatus, ProjectStatus
from src.db.repository.application import ApplicationRepository
from src.db.repository.city import CityRepository
from src.db.repository.event import EventRepository
from src.db.repository.project import ProjectRepository
from src.db.unit_of_work import UnitOfWork
from src.service.user.schema import UserDTO

from .schema import CreateProjectSchema, ProjectDTO, ProjectFilter, UpdateProjectSchema

ALLOWED_PROJECT_STATUS_TRANSITIONS = {
    ProjectStatus.NEW: {
        ProjectStatus.SELECTION_COMPLETED,
        ProjectStatus.STARTED,
        ProjectStatus.CANCELED,
    },
    ProjectStatus.SELECTION_COMPLETED: {
        ProjectStatus.STARTED,
        ProjectStatus.CANCELED,
    },
    ProjectStatus.STARTED: {
        ProjectStatus.ENDED,
        ProjectStatus.CANCELED,
    },
    ProjectStatus.ENDED: set(),
    ProjectStatus.CANCELED: set(),
}


class ProjectService:
    def __init__(
        self,
        uow: UnitOfWork,
        repository: ProjectRepository,
        city_repository: CityRepository,
        event_repository: EventRepository,
        application_repository: ApplicationRepository,
    ):
        self.uow = uow
        self.repository = repository
        self.city_repository = city_repository
        self.event_repository = event_repository
        self.application_repository = application_repository

    async def get_all(self, filters: ProjectFilter) -> list[ProjectDTO]:
        async with self.uow as uow:
            projects = await self.repository.get_multi_out(
                uow.session,
                filters.to_repository_filters(),
            )
            return [ProjectDTO.model_validate(project) for project in projects]

    async def get_by_id(self, project_id: UUID) -> ProjectDTO:
        async with self.uow as uow:
            project = await self._get_by_id_or_raise(uow.session, project_id)
            return ProjectDTO.model_validate(project)

    async def create(self, data: CreateProjectSchema, owner: UserDTO) -> ProjectDTO:
        async with self.uow as uow:
            await self._ensure_city_exists(uow.session, data.city_id)
            await self._ensure_event_exists(uow.session, data.event_id)
            data_to_create = data.model_dump()
            data_to_create["owner_id"] = owner.id
            project = await self.repository.create(uow.session, data_to_create)
            await uow.commit()
            return ProjectDTO.model_validate(project)

    async def update(
        self,
        project_id: UUID,
        data: UpdateProjectSchema,
        user: UserDTO,
    ) -> ProjectDTO:
        async with self.uow as uow:
            project = await self._get_by_id_or_raise(uow.session, project_id)
            self._ensure_owner_or_admin(project.owner_id, user)

            data_to_update = data.model_dump(exclude_unset=True)
            if not data_to_update:
                msg = "Empty update data"
                raise BadRequestError(msg)
            if data_to_update.get("city_id") is not None:
                await self._ensure_city_exists(uow.session, data_to_update["city_id"])
            if data_to_update.get("event_id") is not None:
                await self._ensure_event_exists(uow.session, data_to_update["event_id"])
            status = data_to_update.get("status")
            if status is not None:
                await self._validate_status_transition(uow.session, project, status)
            updated_project = await self.repository.update(
                uow.session,
                project_id,
                data_to_update,
            )
            await uow.commit()
            return ProjectDTO.model_validate(updated_project)

    async def delete(self, project_id: UUID, user: UserDTO) -> None:
        async with self.uow as uow:
            project = await self._get_by_id_or_raise(uow.session, project_id)
            self._ensure_owner_or_admin(project.owner_id, user)
            await self.repository.delete_by_id(uow.session, project_id)
            await uow.commit()

    async def _get_by_id_or_raise(
        self,
        session: AsyncSession,
        project_id: UUID,
    ):
        project = await self.repository.get_out(session, {"id": project_id})
        if not project:
            raise ProjectNotFoundError()
        return project

    async def _ensure_city_exists(
        self,
        session: AsyncSession,
        city_id: UUID | None,
    ) -> None:
        if city_id is None:
            return
        city = await self.city_repository.get(session, {"id": city_id})
        if not city:
            raise CityNotFoundError()

    async def _ensure_event_exists(
        self,
        session: AsyncSession,
        event_id: UUID | None,
    ) -> None:
        if event_id is None:
            return
        event = await self.event_repository.get(session, {"id": event_id})
        if not event:
            raise EventNotFoundError()

    async def _validate_status_transition(
        self,
        session: AsyncSession,
        project,
        target_status: ProjectStatus,
    ) -> None:
        if project.status == target_status:
            return
        allowed_statuses = ALLOWED_PROJECT_STATUS_TRANSITIONS[project.status]
        if target_status not in allowed_statuses:
            msg = f"Cannot change project status from {project.status} to {target_status}"
            raise BadRequestError(msg)
        if target_status == ProjectStatus.SELECTION_COMPLETED:
            await self._ensure_vacancies_filled(session, project)

    async def _ensure_vacancies_filled(self, session: AsyncSession, project) -> None:
        for vacancy in project.vacancies:
            accepted_count = await self.application_repository.count_by_vacancy_status(
                session,
                vacancy.id,
                ApplicationStatus.ACCEPTED,
            )
            if accepted_count < vacancy.required_count:
                msg = (
                    "Cannot complete selection while project vacancies "
                    "do not have enough accepted participants"
                )
                raise BadRequestError(msg)

    def _ensure_owner_or_admin(
        self,
        owner_id: UUID | None,
        user: UserDTO,
    ) -> None:
        if "*" in user.scopes or owner_id == user.id:
            return
        raise NoAccessError()
