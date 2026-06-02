from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions.service.aws import ImageNotFoundError
from src.core.exceptions.service.base import BadRequestError
from src.core.exceptions.service.organization import (
    OrganizationAlreadyExistsError,
    OrganizationNotFoundError,
)
from src.core.exceptions.service.user import UserNotFoundError
from src.db.models import Organization
from src.db.repository.image import OrganizationImageUrlRepository
from src.db.repository.organization import OrganizationRepository
from src.db.repository.role import RoleRepository
from src.db.repository.user import UserRepository
from src.db.unit_of_work import UnitOfWork
from src.service.image_upload.service import ImageUploadService

from .schema import (
    CreateOrganizationSchema,
    OrganizationDTO,
    OrganizationFilter,
    OrganizationImageUrlDTO,
    UpdateOrganizationSchema,
)


class OrganizationService:
    def __init__(
        self,
        uow: UnitOfWork,
        repository: OrganizationRepository,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        image_repository: OrganizationImageUrlRepository,
    ):
        self.uow = uow
        self.repository = repository
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.image_repository = image_repository

    async def get_all(self, filters: OrganizationFilter) -> list[OrganizationDTO]:
        async with self.uow as uow:
            organizations = await self.repository.get_multi_out(
                uow.session,
                filters.to_repository_filters(),
                order_by=(Organization.name.asc(),),
            )
            return [
                OrganizationDTO.model_validate(organization)
                for organization in organizations
            ]

    async def get_by_id(self, organization_id: UUID) -> OrganizationDTO:
        async with self.uow as uow:
            organization = await self._get_by_id_or_raise(
                uow.session,
                organization_id,
            )
            return OrganizationDTO.model_validate(organization)

    async def create(self, data: CreateOrganizationSchema) -> OrganizationDTO:
        async with self.uow as uow:
            await self._ensure_name_is_unique(uow.session, data.name)
            if data.owner_user_id is not None:
                await self._ensure_user_exists(uow.session, data.owner_user_id)

            organization = await self.repository.create(
                uow.session,
                data.model_dump(),
            )
            if data.owner_user_id is not None:
                await self._assign_organizer_role(uow.session, data.owner_user_id)

            await uow.commit()
            created_organization = await self._get_by_id_or_raise(
                uow.session,
                organization.id,
            )
            return OrganizationDTO.model_validate(created_organization)

    async def update(
        self,
        organization_id: UUID,
        data: UpdateOrganizationSchema,
    ) -> OrganizationDTO:
        async with self.uow as uow:
            organization = await self._get_by_id_or_raise(
                uow.session,
                organization_id,
            )
            data_to_update = data.model_dump(exclude_unset=True)
            if not data_to_update:
                msg = "Empty update data"
                raise BadRequestError(msg)

            if "name" in data_to_update and data_to_update["name"] != organization.name:
                await self._ensure_name_is_unique(uow.session, data_to_update["name"])
            if data_to_update.get("owner_user_id") is not None:
                await self._ensure_user_exists(
                    uow.session, data_to_update["owner_user_id"]
                )

            await self.repository.update(uow.session, organization_id, data_to_update)
            owner_user_id = data_to_update.get("owner_user_id")
            if owner_user_id is not None:
                await self._assign_organizer_role(uow.session, owner_user_id)

            await uow.commit()
            updated_organization = await self._get_by_id_or_raise(
                uow.session,
                organization_id,
            )
            return OrganizationDTO.model_validate(updated_organization)

    async def delete(self, organization_id: UUID) -> None:
        async with self.uow as uow:
            organization = await self._get_by_id_or_raise(uow.session, organization_id)
            for image in organization.images:
                await ImageUploadService.delete_image(image.url)
            await self.repository.delete_by_id(uow.session, organization_id)
            await uow.commit()

    async def upload_image(
        self,
        organization_id: UUID,
        image_data: bytes,
        file_name: str | None,
        content_type: str | None,
    ) -> OrganizationImageUrlDTO:
        async with self.uow as uow:
            await self._get_by_id_or_raise(uow.session, organization_id)
            image_url = await ImageUploadService.upload_image(
                image_data,
                file_name,
                content_type,
                folder="organizations",
            )
            try:
                image = await self.image_repository.create(
                    uow.session,
                    {"organization_id": organization_id, "url": image_url},
                )
                await uow.commit()
                return OrganizationImageUrlDTO.model_validate(image)
            except Exception:
                await ImageUploadService.delete_image(image_url)
                raise

    async def delete_image(
        self,
        organization_id: UUID,
        image_id: UUID,
    ) -> None:
        async with self.uow as uow:
            await self._get_by_id_or_raise(uow.session, organization_id)
            image = await self.image_repository.get(
                uow.session,
                {"id": image_id, "organization_id": organization_id},
            )
            if not image:
                raise ImageNotFoundError()
            await ImageUploadService.delete_image(image.url)
            await self.image_repository.delete_by_id(uow.session, image_id)
            await uow.commit()

    async def _get_by_id_or_raise(
        self,
        session: AsyncSession,
        organization_id: UUID,
    ):
        organization = await self.repository.get_out(session, {"id": organization_id})
        if not organization:
            raise OrganizationNotFoundError()
        return organization

    async def _ensure_name_is_unique(self, session: AsyncSession, name: str) -> None:
        existing = await self.repository.get(session, {"name": name})
        if existing:
            raise OrganizationAlreadyExistsError()

    async def _ensure_user_exists(self, session: AsyncSession, user_id: UUID) -> None:
        user = await self.user_repository.get(session, {"id": user_id})
        if not user:
            raise UserNotFoundError()

    async def _assign_organizer_role(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> None:
        role = await self.role_repository.get(
            session,
            {"name": settings.rbac.organizer_role_name},
        )
        if not role:
            msg = "Organizer role is not configured"
            raise BadRequestError(msg)
        await self.user_repository.assign_roles(session, user_id, [role.id])
