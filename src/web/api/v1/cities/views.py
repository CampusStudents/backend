from uuid import UUID

from fastapi import APIRouter, Security, status

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.city.schema import CityDTO, CreateCitySchema, UpdateCitySchema
from src.web.api.dependencies import (
    CityServiceDep,
    get_current_active_user,
)

router = APIRouter(prefix=settings.api.v1.cities)


@router.get(
    "/",
    dependencies=[Security(get_current_active_user, scopes=[Scope.CITIES_LIST])],
)
async def get_cities(
    service: CityServiceDep,
) -> list[CityDTO]:
    return await service.get_all()


@router.get(
    "/{city_id}",
    dependencies=[Security(get_current_active_user, scopes=[Scope.CITIES_DETAIL])],
)
async def get_city(
    city_id: UUID,
    service: CityServiceDep,
) -> CityDTO:
    return await service.get_by_id(city_id)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(get_current_active_user, scopes=[Scope.CITIES_CREATE])],
)
async def create_city(
    data: CreateCitySchema,
    service: CityServiceDep,
) -> CityDTO:
    return await service.create(data)


@router.patch(
    "/{city_id}",
    dependencies=[Security(get_current_active_user, scopes=[Scope.CITIES_UPDATE])],
)
async def update_city(
    city_id: UUID,
    data: UpdateCitySchema,
    service: CityServiceDep,
) -> CityDTO:
    return await service.update(city_id, data)


@router.delete(
    "/{city_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Security(get_current_active_user, scopes=[Scope.CITIES_DELETE])],
)
async def delete_city(
    city_id: UUID,
    service: CityServiceDep,
) -> None:
    await service.delete(city_id)
