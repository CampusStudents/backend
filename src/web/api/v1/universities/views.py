from uuid import UUID

from fastapi import APIRouter, Security, status

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.university.schema import (
    CreateUniversitySchema,
    UniversityDTO,
    UpdateUniversitySchema,
)
from src.web.api.dependencies import (
    UniversityServiceDep,
    get_current_active_user,
)

router = APIRouter(prefix=settings.api.v1.universities)


@router.get(
    "/",
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.UNIVERSITIES_LIST]),
    ],
)
async def get_universities(
    service: UniversityServiceDep,
) -> list[UniversityDTO]:
    return await service.get_all()


@router.get(
    "/{university_id}",
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.UNIVERSITIES_DETAIL]),
    ],
)
async def get_university(
    university_id: UUID,
    service: UniversityServiceDep,
) -> UniversityDTO:
    return await service.get_by_id(university_id)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.UNIVERSITIES_CREATE]),
    ],
)
async def create_university(
    data: CreateUniversitySchema,
    service: UniversityServiceDep,
) -> UniversityDTO:
    return await service.create(data)


@router.patch(
    "/{university_id}",
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.UNIVERSITIES_UPDATE]),
    ],
)
async def update_university(
    university_id: UUID,
    data: UpdateUniversitySchema,
    service: UniversityServiceDep,
) -> UniversityDTO:
    return await service.update(university_id, data)


@router.delete(
    "/{university_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.UNIVERSITIES_DELETE]),
    ],
)
async def delete_university(
    university_id: UUID,
    service: UniversityServiceDep,
) -> None:
    await service.delete(university_id)
