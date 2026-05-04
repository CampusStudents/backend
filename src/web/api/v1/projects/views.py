from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Security, status

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.application.schema import (
    ApplicationDecisionSchema,
    ApplicationDTO,
    CreateApplicationSchema,
)
from src.service.project.schema import (
    CreateProjectSchema,
    ProjectDTO,
    ProjectFilter,
    UpdateProjectSchema,
)
from src.service.project_vacancy.schema import (
    CreateProjectVacancySchema,
    ProjectVacancyDTO,
    ProjectVacancyFilter,
    UpdateProjectVacancySchema,
)
from src.service.user.schema import UserDTO
from src.web.api.dependencies import (
    ApplicationServiceDep,
    ProjectServiceDep,
    ProjectVacancyServiceDep,
    get_current_active_user,
    get_current_active_user_with_profile,
)

router = APIRouter(prefix=settings.api.v1.projects)


@router.get(
    "/",
    dependencies=[Security(get_current_active_user, scopes=[Scope.PROJECTS_LIST])],
)
async def get_projects(
    service: ProjectServiceDep,
    filters: Annotated[ProjectFilter, Query()],
) -> list[ProjectDTO]:
    return await service.get_all(filters)


@router.get(
    "/{project_id}",
    dependencies=[Security(get_current_active_user, scopes=[Scope.PROJECTS_DETAIL])],
)
async def get_project(
    project_id: UUID,
    service: ProjectServiceDep,
) -> ProjectDTO:
    return await service.get_by_id(project_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_project(
    data: CreateProjectSchema,
    service: ProjectServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.PROJECTS_CREATE],
    ),
) -> ProjectDTO:
    return await service.create(data, user)


@router.patch("/{project_id}")
async def update_project(
    project_id: UUID,
    data: UpdateProjectSchema,
    service: ProjectServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.PROJECTS_UPDATE],
    ),
) -> ProjectDTO:
    return await service.update(project_id, data, user)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    service: ProjectServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.PROJECTS_DELETE],
    ),
) -> None:
    await service.delete(project_id, user)


@router.get(
    "/{project_id}/vacancies",
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.PROJECT_VACANCIES_LIST]),
    ],
)
async def get_project_vacancies(
    project_id: UUID,
    service: ProjectVacancyServiceDep,
    filters: Annotated[ProjectVacancyFilter, Query()],
) -> list[ProjectVacancyDTO]:
    return await service.get_by_project_id(project_id, filters)


@router.get(
    "/{project_id}/vacancies/{vacancy_id}",
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.PROJECT_VACANCIES_DETAIL]),
    ],
)
async def get_project_vacancy(
    project_id: UUID,
    vacancy_id: UUID,
    service: ProjectVacancyServiceDep,
) -> ProjectVacancyDTO:
    return await service.get_by_id(project_id, vacancy_id)


@router.post("/{project_id}/vacancies", status_code=status.HTTP_201_CREATED)
async def create_project_vacancy(
    project_id: UUID,
    data: CreateProjectVacancySchema,
    service: ProjectVacancyServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.PROJECT_VACANCIES_CREATE],
    ),
) -> ProjectVacancyDTO:
    return await service.create(project_id, data, user)


@router.patch("/{project_id}/vacancies/{vacancy_id}")
async def update_project_vacancy(
    project_id: UUID,
    vacancy_id: UUID,
    data: UpdateProjectVacancySchema,
    service: ProjectVacancyServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.PROJECT_VACANCIES_UPDATE],
    ),
) -> ProjectVacancyDTO:
    return await service.update(project_id, vacancy_id, data, user)


@router.delete(
    "/{project_id}/vacancies/{vacancy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project_vacancy(
    project_id: UUID,
    vacancy_id: UUID,
    service: ProjectVacancyServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.PROJECT_VACANCIES_DELETE],
    ),
) -> None:
    await service.delete(project_id, vacancy_id, user)


@router.post(
    "/{project_id}/vacancies/{vacancy_id}/applications",
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    project_id: UUID,
    vacancy_id: UUID,
    data: CreateApplicationSchema,
    service: ApplicationServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.APPLICATIONS_CREATE],
    ),
) -> ApplicationDTO:
    return await service.create(project_id, vacancy_id, data, user)


@router.get("/{project_id}/vacancies/{vacancy_id}/applications")
async def get_project_vacancy_applications(
    project_id: UUID,
    vacancy_id: UUID,
    service: ApplicationServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.APPLICATIONS_LIST],
    ),
) -> list[ApplicationDTO]:
    return await service.get_by_project_vacancy(project_id, vacancy_id, user)


@router.patch("/{project_id}/vacancies/{vacancy_id}/applications/{application_id}")
async def decide_application(  # noqa: PLR0913
    project_id: UUID,
    vacancy_id: UUID,
    application_id: UUID,
    data: ApplicationDecisionSchema,
    service: ApplicationServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.APPLICATIONS_UPDATE],
    ),
) -> ApplicationDTO:
    return await service.decide(project_id, vacancy_id, application_id, data, user)
