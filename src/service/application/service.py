from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.service.application import (
    ApplicationAlreadyExistsError,
    ApplicationNotFoundError,
    ApplicationStatusTransitionError,
    ProjectNotAcceptingApplicationsError,
    ProjectOwnerApplicationError,
)
from src.core.exceptions.service.base import NoAccessError
from src.core.exceptions.service.project import ProjectNotFoundError
from src.core.exceptions.service.project_vacancy import ProjectVacancyNotFoundError
from src.db.choices import ApplicationStatus, ProjectStatus
from src.db.models import Application
from src.db.repository.application import ApplicationRepository
from src.db.repository.project import ProjectRepository
from src.db.repository.project_vacancy import ProjectVacancyRepository
from src.db.unit_of_work import UnitOfWork
from src.service.user.schema import UserDTO

from .schema import ApplicationDecisionSchema, ApplicationDTO, CreateApplicationSchema

APPLICATION_CLOSED_PROJECT_STATUSES = {
    ProjectStatus.ENDED,
    ProjectStatus.CANCELED,
}


class ApplicationService:
    def __init__(
        self,
        uow: UnitOfWork,
        repository: ApplicationRepository,
        project_repository: ProjectRepository,
        vacancy_repository: ProjectVacancyRepository,
    ):
        self.uow = uow
        self.repository = repository
        self.project_repository = project_repository
        self.vacancy_repository = vacancy_repository

    async def create(
        self,
        project_id: UUID,
        vacancy_id: UUID,
        data: CreateApplicationSchema,
        applicant: UserDTO,
    ) -> ApplicationDTO:
        async with self.uow as uow:
            project = await self._get_project_or_raise(uow.session, project_id)
            vacancy = await self._get_project_vacancy_or_raise(
                uow.session,
                project_id,
                vacancy_id,
            )
            if project.status in APPLICATION_CLOSED_PROJECT_STATUSES:
                raise ProjectNotAcceptingApplicationsError()
            if project.owner_id == applicant.id:
                raise ProjectOwnerApplicationError()
            existing = await self.repository.get(
                uow.session,
                {"vacancy_id": vacancy.id, "applicant_id": applicant.id},
            )
            if existing:
                raise ApplicationAlreadyExistsError()

            application = await self.repository.create(
                uow.session,
                {
                    "vacancy_id": vacancy.id,
                    "applicant_id": applicant.id,
                    "cover_letter": data.cover_letter,
                    "status": ApplicationStatus.PENDING,
                },
            )
            await uow.commit()

            created_application = await self._get_by_id_or_raise(
                uow.session,
                application.id,
            )
            return ApplicationDTO.model_validate(created_application)

    async def get_my_applications(self, applicant: UserDTO) -> list[ApplicationDTO]:
        async with self.uow as uow:
            applications = await self.repository.get_multi_out(
                uow.session,
                {"applicant_id": applicant.id},
                order_by=(Application.created_at.desc(),),
            )
            return [
                ApplicationDTO.model_validate(application)
                for application in applications
            ]

    async def get_by_project_vacancy(
        self,
        project_id: UUID,
        vacancy_id: UUID,
        user: UserDTO,
    ) -> list[ApplicationDTO]:
        async with self.uow as uow:
            project = await self._get_project_or_raise(uow.session, project_id)
            self._ensure_owner_or_admin(project.owner_id, user)
            vacancy = await self._get_project_vacancy_or_raise(
                uow.session,
                project_id,
                vacancy_id,
            )
            applications = await self.repository.get_multi_out(
                uow.session,
                {"vacancy_id": vacancy.id},
                order_by=(Application.created_at.desc(),),
            )
            return [
                ApplicationDTO.model_validate(application)
                for application in applications
            ]

    async def decide(
        self,
        project_id: UUID,
        vacancy_id: UUID,
        application_id: UUID,
        data: ApplicationDecisionSchema,
        user: UserDTO,
    ) -> ApplicationDTO:
        async with self.uow as uow:
            project = await self._get_project_or_raise(uow.session, project_id)
            self._ensure_owner_or_admin(project.owner_id, user)
            await self._get_project_vacancy_or_raise(
                uow.session,
                project_id,
                vacancy_id,
            )
            application = await self._get_by_id_or_raise(uow.session, application_id)
            if application.vacancy_id != vacancy_id:
                raise ApplicationNotFoundError()
            if application.status != ApplicationStatus.PENDING:
                raise ApplicationStatusTransitionError()

            await self.repository.update(
                uow.session,
                application.id,
                {
                    "status": data.status,
                    "decided_at": datetime.now(UTC).replace(tzinfo=None),
                },
            )
            await uow.commit()

            updated_application = await self._get_by_id_or_raise(
                uow.session,
                application.id,
            )
            return ApplicationDTO.model_validate(updated_application)

    async def withdraw(
        self, application_id: UUID, applicant: UserDTO
    ) -> ApplicationDTO:
        async with self.uow as uow:
            application = await self._get_by_id_or_raise(uow.session, application_id)
            if application.applicant_id != applicant.id:
                raise NoAccessError()
            if application.status != ApplicationStatus.PENDING:
                raise ApplicationStatusTransitionError()

            await self.repository.update(
                uow.session,
                application.id,
                {
                    "status": ApplicationStatus.WITHDRAWN,
                    "decided_at": datetime.now(UTC).replace(tzinfo=None),
                },
            )
            await uow.commit()

            updated_application = await self._get_by_id_or_raise(
                uow.session,
                application.id,
            )
            return ApplicationDTO.model_validate(updated_application)

    async def _get_project_or_raise(self, session: AsyncSession, project_id: UUID):
        project = await self.project_repository.get(session, {"id": project_id})
        if not project:
            raise ProjectNotFoundError()
        return project

    async def _get_project_vacancy_or_raise(
        self,
        session: AsyncSession,
        project_id: UUID,
        vacancy_id: UUID,
    ):
        vacancy = await self.vacancy_repository.get(
            session,
            {"id": vacancy_id, "project_id": project_id},
        )
        if not vacancy:
            raise ProjectVacancyNotFoundError()
        return vacancy

    async def _get_by_id_or_raise(
        self,
        session: AsyncSession,
        application_id: UUID,
    ):
        application = await self.repository.get_out(session, {"id": application_id})
        if not application:
            raise ApplicationNotFoundError()
        return application

    def _ensure_owner_or_admin(
        self,
        owner_id: UUID | None,
        user: UserDTO,
    ) -> None:
        if "*" in user.scopes or owner_id == user.id:
            return
        raise NoAccessError()
