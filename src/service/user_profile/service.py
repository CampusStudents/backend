from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.service.base import AlreadyExistsError
from src.core.exceptions.service.city import CityNotFoundError
from src.core.exceptions.service.university import UniversityNotFoundError
from src.core.exceptions.service.user import UserNotFoundError
from src.core.exceptions.service.user_profile import UserProfileNotFoundError
from src.db.repository.city import CityRepository
from src.db.repository.university import UniversityRepository
from src.db.repository.user import UserRepository
from src.db.repository.user_profile import UserProfileRepository
from src.db.unit_of_work import UnitOfWork

from .schema import CreateUserProfileSchema, UpdateUserProfileSchema, UserProfileDTO


class UserProfileService:
    def __init__(
        self,
        uow: UnitOfWork,
        repository: UserProfileRepository,
        user_repository: UserRepository,
        city_repository: CityRepository,
        university_repository: UniversityRepository,
    ):
        self.uow = uow
        self.repository = repository
        self.user_repository = user_repository
        self.city_repository = city_repository
        self.university_repository = university_repository

    async def get_current_user_profile(self, user_id: UUID) -> UserProfileDTO:
        async with self.uow as uow:
            profile = await self._get_by_user_id_or_raise(uow.session, user_id)
            return UserProfileDTO.model_validate(profile)

    async def get_by_user_id(self, user_id: UUID) -> UserProfileDTO:
        async with self.uow as uow:
            await self._ensure_user_exists(uow.session, user_id)
            profile = await self._get_by_user_id_or_raise(uow.session, user_id)
            return UserProfileDTO.model_validate(profile)

    async def create(
        self,
        user_id: UUID,
        data: CreateUserProfileSchema,
    ) -> UserProfileDTO:
        async with self.uow as uow:
            existing_profile = await self.repository.get_out(
                uow.session,
                {"user_id": user_id},
            )
            if existing_profile:
                raise AlreadyExistsError("User profile already exists")

            data_to_create = data.model_dump()
            await self._ensure_related_entities_exist(uow.session, data_to_create)
            data_to_create["user_id"] = user_id
            profile = await self.repository.create(
                uow.session,
                data_to_create,
            )
            await self.user_repository.update(
                uow.session,
                user_id,
                {"is_profile_completed": True},
            )
            await uow.commit()
            return UserProfileDTO.model_validate(profile)

    async def update(
        self,
        user_id: UUID,
        data: UpdateUserProfileSchema,
    ) -> UserProfileDTO:
        async with self.uow as uow:
            profile = await self._get_by_user_id_or_raise(uow.session, user_id)
            data_to_update = data.model_dump(exclude_unset=True)
            await self._ensure_related_entities_exist(uow.session, data_to_update)
            updated_profile = await self.repository.update(
                uow.session,
                profile.id,
                data_to_update,
            )
            await self.user_repository.update(
                uow.session,
                user_id,
                {"is_profile_completed": True},
            )
            await uow.commit()
            return UserProfileDTO.model_validate(updated_profile or profile)

    async def _get_by_user_id_or_raise(
        self,
        session: AsyncSession,
        user_id: UUID,
    ):
        profile = await self.repository.get_out(session, {"user_id": user_id})
        if not profile:
            raise UserProfileNotFoundError()
        return profile

    async def _ensure_user_exists(self, session: AsyncSession, user_id: UUID) -> None:
        user = await self.user_repository.get(session, {"id": user_id})
        if not user:
            raise UserNotFoundError()

    async def _ensure_related_entities_exist(
        self,
        session: AsyncSession,
        data: dict,
    ) -> None:
        city_id = data.get("city_id")
        university_id = data.get("university_id")

        if city_id is not None:
            city = await self.city_repository.get(session, {"id": city_id})
            if not city:
                raise CityNotFoundError()

        if university_id is not None:
            university = await self.university_repository.get(
                session,
                {"id": university_id},
            )
            if not university:
                raise UniversityNotFoundError()
