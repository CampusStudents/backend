from uuid import UUID

from fastapi import APIRouter, Security, status

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.city.schema import CityDTO, CreateCitySchema, UpdateCitySchema
from src.service.user.schema import UserDTO
from src.web.api.dependencies import (
    CityServiceDep,
    get_current_active_user,
)

router = APIRouter(prefix=settings.api.v1.cities)


@router.get("/")
async def get_cities(
    service: CityServiceDep,
    _: UserDTO = Security(get_current_active_user, scopes=[Scope.CITIES_LIST]),
) -> list[CityDTO]:
    return await service.get_all()


@router.get("/{city_id}")
async def get_city(
    city_id: UUID,
    service: CityServiceDep,
    _: UserDTO = Security(get_current_active_user, scopes=[Scope.CITIES_DETAIL]),
) -> CityDTO:
    return await service.get_by_id(city_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_city(
    data: CreateCitySchema,
    service: CityServiceDep,
    _: UserDTO = Security(get_current_active_user, scopes=[Scope.CITIES_CREATE]),
) -> CityDTO:
    return await service.create(data)


@router.put("/{city_id}")
async def update_city(
    city_id: UUID,
    data: UpdateCitySchema,
    service: CityServiceDep,
    _: UserDTO = Security(get_current_active_user, scopes=[Scope.CITIES_UPDATE]),
) -> CityDTO:
    return await service.update(city_id, data)


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_city(
    city_id: UUID,
    service: CityServiceDep,
    _: UserDTO = Security(get_current_active_user, scopes=[Scope.CITIES_DELETE]),
) -> None:
    await service.delete(city_id)
