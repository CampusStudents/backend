from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.service.city import CityNotFoundError
from src.core.exceptions.service.university import UniversityNotFoundError
from src.db.repository.city import CityRepository
from src.db.repository.university import UniversityRepository
from src.db.unit_of_work import UnitOfWork

from .schema import (
    CreateUniversitySchema,
    UniversityDTO,
    UniversityFilter,
    UpdateUniversitySchema,
)


class UniversityService:
    def __init__(
        self,
        uow: UnitOfWork,
        repository: UniversityRepository,
        city_repository: CityRepository,
    ):
        self.uow = uow
        self.repository = repository
        self.city_repository = city_repository

    async def get_all(self, filters: UniversityFilter) -> list[UniversityDTO]:
        async with self.uow as uow:
            universities = await self.repository.get_multi(
                uow.session,
                filters.to_repository_filters(),
            )
            return [
                UniversityDTO.model_validate(university) for university in universities
            ]

    async def get_by_id(self, university_id: UUID) -> UniversityDTO:
        async with self.uow as uow:
            university = await self._get_by_id_or_raise(uow.session, university_id)
            return UniversityDTO.model_validate(university)

    async def create(self, data: CreateUniversitySchema) -> UniversityDTO:
        async with self.uow as uow:
            await self._ensure_city_exists(uow.session, data.city_id)
            university = await self.repository.create(
                uow.session,
                data.model_dump(),
            )
            await uow.commit()
            return UniversityDTO.model_validate(university)

    async def update(
        self,
        university_id: UUID,
        data: UpdateUniversitySchema,
    ) -> UniversityDTO:
        async with self.uow as uow:
            university = await self._get_by_id_or_raise(uow.session, university_id)
            data_to_update = data.model_dump(exclude_unset=True)
            if data_to_update.get("city_id") is not None:
                await self._ensure_city_exists(uow.session, data_to_update["city_id"])
            updated_university = await self.repository.update(
                uow.session,
                university_id,
                data_to_update,
            )
            await uow.commit()
            return UniversityDTO.model_validate(updated_university or university)

    async def delete(self, university_id: UUID) -> None:
        async with self.uow as uow:
            await self._get_by_id_or_raise(uow.session, university_id)
            await self.repository.delete_by_id(uow.session, university_id)
            await uow.commit()

    async def _get_by_id_or_raise(
        self,
        session: AsyncSession,
        university_id: UUID,
    ):
        university = await self.repository.get(session, {"id": university_id})
        if not university:
            raise UniversityNotFoundError()
        return university

    async def _ensure_city_exists(
        self,
        session: AsyncSession,
        city_id: UUID,
    ) -> None:
        city = await self.city_repository.get(session, {"id": city_id})
        if not city:
            raise CityNotFoundError()
