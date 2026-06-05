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
from src.service.team_member.schema import TeamMemberDTO
from src.service.user.schema import UserDTO
from src.web.api.dependencies import (
    ApplicationServiceDep,
    ProjectServiceDep,
    ProjectVacancyServiceDep,
    TeamMemberServiceDep,
    get_current_active_user,
    get_current_active_user_with_profile,
)

router = APIRouter(prefix=settings.api.v1.projects)


@router.get("/")
async def get_projects(
    service: ProjectServiceDep,
    filters: Annotated[ProjectFilter, Query()],
) -> list[ProjectDTO]:
    return await service.get_all(filters)


@router.get("/favorites")
async def get_favorite_projects(
    service: ProjectServiceDep,
    filters: Annotated[ProjectFilter, Query()],
    user: UserDTO = Security(
        get_current_active_user,
        scopes=[Scope.PROJECTS_FAVORITES_LIST],
    ),
) -> list[ProjectDTO]:
    return await service.get_favorite_projects(filters, user)


@router.get("/{project_id}")
async def get_project(
    project_id: UUID,
    service: ProjectServiceDep,
) -> ProjectDTO:
    return await service.get_by_id(project_id)


@router.post("/{project_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def add_project_to_favorites(
    project_id: UUID,
    service: ProjectServiceDep,
    user: UserDTO = Security(
        get_current_active_user,
        scopes=[Scope.PROJECTS_FAVORITES_UPDATE],
    ),
) -> None:
    await service.add_to_favorites(project_id, user)


@router.delete("/{project_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_from_favorites(
    project_id: UUID,
    service: ProjectServiceDep,
    user: UserDTO = Security(
        get_current_active_user,
        scopes=[Scope.PROJECTS_FAVORITES_UPDATE],
    ),
) -> None:
    await service.remove_from_favorites(project_id, user)


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


@router.get("/{project_id}/team")
async def get_project_team(
    project_id: UUID,
    service: TeamMemberServiceDep,
    _: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.TEAM_MEMBERS_LIST],
    ),
) -> list[TeamMemberDTO]:
    return await service.get_by_project(project_id)


@router.get(
    "/{project_id}/vacancies",
)
async def get_project_vacancies(
    project_id: UUID,
    service: ProjectVacancyServiceDep,
    filters: Annotated[ProjectVacancyFilter, Query()],
) -> list[ProjectVacancyDTO]:
    return await service.get_by_project_id(project_id, filters)


@router.get(
    "/{project_id}/vacancies/{vacancy_id}",
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
async def decide_application(
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
