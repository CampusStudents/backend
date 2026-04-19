from uuid import UUID

from fastapi import APIRouter, Security, status

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.university.schema import (
    CreateUniversitySchema,
    UniversityDTO,
    UpdateUniversitySchema,
)
from src.service.user.schema import UserDTO
from src.web.api.dependencies import (
    UniversityServiceDep,
    get_current_active_user,
)

router = APIRouter(prefix=settings.api.v1.universities)


@router.get("/")
async def get_universities(
    service: UniversityServiceDep,
    _: UserDTO = Security(get_current_active_user, scopes=[Scope.UNIVERSITIES_LIST]),
) -> list[UniversityDTO]:
    return await service.get_all()


@router.get("/{university_id}")
async def get_university(
    university_id: UUID,
    service: UniversityServiceDep,
    _: UserDTO = Security(get_current_active_user, scopes=[Scope.UNIVERSITIES_DETAIL]),
) -> UniversityDTO:
    return await service.get_by_id(university_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_university(
    data: CreateUniversitySchema,
    service: UniversityServiceDep,
    _: UserDTO = Security(get_current_active_user, scopes=[Scope.UNIVERSITIES_CREATE]),
) -> UniversityDTO:
    return await service.create(data)


@router.put("/{university_id}")
async def update_university(
    university_id: UUID,
    data: UpdateUniversitySchema,
    service: UniversityServiceDep,
    _: UserDTO = Security(get_current_active_user, scopes=[Scope.UNIVERSITIES_UPDATE]),
) -> UniversityDTO:
    return await service.update(university_id, data)


@router.delete("/{university_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_university(
    university_id: UUID,
    service: UniversityServiceDep,
    _: UserDTO = Security(get_current_active_user, scopes=[Scope.UNIVERSITIES_DELETE]),
) -> None:
    await service.delete(university_id)
