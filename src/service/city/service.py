from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.service.base import AlreadyExistsError
from src.core.exceptions.service.city import CityNotFoundError
from src.db.repository.city import CityRepository
from src.db.unit_of_work import UnitOfWork

from .schema import CityDTO, CreateCitySchema, UpdateCitySchema


class CityService:
    def __init__(self, uow: UnitOfWork, repository: CityRepository):
        self.uow = uow
        self.repository = repository

    async def get_all(self) -> list[CityDTO]:
        async with self.uow as uow:
            cities = await self.repository.get_multi(uow.session)
            return [CityDTO.model_validate(city) for city in cities]

    async def get_by_id(self, city_id: UUID) -> CityDTO:
        async with self.uow as uow:
            city = await self._get_by_id_or_raise(uow.session, city_id)
            return CityDTO.model_validate(city)

    async def create(self, data: CreateCitySchema) -> CityDTO:
        async with self.uow as uow:
            await self._ensure_name_is_unique(uow.session, data.name)
            city = await self.repository.create(uow.session, {"name": data.name})
            await uow.commit()
            return CityDTO.model_validate(city)

    async def update(self, city_id: UUID, data: UpdateCitySchema) -> CityDTO:
        async with self.uow as uow:
            city = await self._get_by_id_or_raise(uow.session, city_id)
            data_to_update = data.model_dump(exclude_unset=True)
            if "name" in data_to_update and city.name != data_to_update["name"]:
                await self._ensure_name_is_unique(uow.session, data_to_update["name"])

            updated_city = await self.repository.update(
                uow.session,
                city_id,
                data_to_update,
            )
            await uow.commit()
            return CityDTO.model_validate(updated_city or city)

    async def delete(self, city_id: UUID) -> None:
        async with self.uow as uow:
            await self._get_by_id_or_raise(uow.session, city_id)
            await self.repository.delete_by_id(uow.session, city_id)
            await uow.commit()

    async def _get_by_id_or_raise(self, session: AsyncSession, city_id: UUID):
        city = await self.repository.get(session, {"id": city_id})
        if not city:
            raise CityNotFoundError()
        return city

    async def _ensure_name_is_unique(self, session: AsyncSession, name: str) -> None:
        existing_city = await self.repository.get_out(session, {"name": name})
        if existing_city:
            raise AlreadyExistsError("City already exists")
