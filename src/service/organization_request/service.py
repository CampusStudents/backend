from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions.service.base import AlreadyExistsError, BadRequestError
from src.core.exceptions.service.organization import OrganizationAlreadyExistsError
from src.core.exceptions.service.organization_request import (
    OrganizationRequestNotFoundError,
    OrganizationRequestStatusError,
)
from src.db.choices import OrganizationRequestStatus
from src.db.models import OrganizationRequest
from src.db.repository.organization import OrganizationRepository
from src.db.repository.organization_request import OrganizationRequestRepository
from src.db.repository.role import RoleRepository
from src.db.repository.user import UserRepository
from src.db.unit_of_work import UnitOfWork
from src.service.user.schema import UserDTO

from .schema import (
    CreateOrganizationRequestSchema,
    OrganizationRequestDTO,
    OrganizationRequestFilter,
    RejectOrganizationRequestSchema,
)


class OrganizationRequestService:
    def __init__(
        self,
        uow: UnitOfWork,
        repository: OrganizationRequestRepository,
        organization_repository: OrganizationRepository,
        role_repository: RoleRepository,
        user_repository: UserRepository,
    ):
        self.uow = uow
        self.repository = repository
        self.organization_repository = organization_repository
        self.role_repository = role_repository
        self.user_repository = user_repository

    async def create(
        self,
        data: CreateOrganizationRequestSchema,
        user: UserDTO,
    ) -> OrganizationRequestDTO:
        async with self.uow as uow:
            existing = await self.repository.get(
                uow.session,
                {
                    "user_id": user.id,
                    "status": OrganizationRequestStatus.PENDING,
                },
            )
            if existing:
                msg = "User already has a pending organization request"
                raise AlreadyExistsError(msg)

            request = await self.repository.create(
                uow.session,
                {
                    **data.model_dump(),
                    "user_id": user.id,
                    "status": OrganizationRequestStatus.PENDING,
                },
            )
            await uow.commit()
            created_request = await self._get_by_id_or_raise(
                uow.session,
                request.id,
            )
            return OrganizationRequestDTO.model_validate(created_request)

    async def get_my_requests(self, user: UserDTO) -> list[OrganizationRequestDTO]:
        async with self.uow as uow:
            requests = await self.repository.get_multi_out(
                uow.session,
                {"user_id": user.id},
                order_by=(OrganizationRequest.created_at.desc(),),
            )
            return [
                OrganizationRequestDTO.model_validate(request)
                for request in requests
            ]

    async def get_all(
        self,
        filters: OrganizationRequestFilter,
    ) -> list[OrganizationRequestDTO]:
        async with self.uow as uow:
            requests = await self.repository.get_multi_out(
                uow.session,
                filters.to_repository_filters(),
                order_by=(OrganizationRequest.created_at.desc(),),
            )
            return [
                OrganizationRequestDTO.model_validate(request)
                for request in requests
            ]

    async def approve(
        self,
        request_id: UUID,
        admin: UserDTO,
    ) -> OrganizationRequestDTO:
        async with self.uow as uow:
            request = await self._get_by_id_or_raise(uow.session, request_id)
            self._ensure_pending(request)
            await self._ensure_organization_name_is_unique(
                uow.session,
                request.organization_name,
            )

            organization = await self.organization_repository.create(
                uow.session,
                {
                    "owner_user_id": request.user_id,
                    "name": request.organization_name,
                    "description": request.description,
                    "contact_email": request.contact_email,
                },
            )
            if not organization:
                msg = "Organization was not created"
                raise BadRequestError(msg)

            organizer_role = await self.role_repository.get(
                uow.session,
                {"name": settings.rbac.organizer_role_name},
            )
            if not organizer_role:
                msg = "Organizer role is not configured"
                raise BadRequestError(msg)
            await self.user_repository.assign_roles(
                uow.session,
                request.user_id,
                [organizer_role.id],
            )

            await self.repository.update(
                uow.session,
                request.id,
                {
                    "status": OrganizationRequestStatus.APPROVED,
                    "reviewed_by_id": admin.id,
                    "reviewed_at": self._now(),
                    "reject_reason": None,
                },
            )
            await uow.commit()
            updated_request = await self._get_by_id_or_raise(uow.session, request.id)
            return OrganizationRequestDTO.model_validate(updated_request)

    async def reject(
        self,
        request_id: UUID,
        data: RejectOrganizationRequestSchema,
        admin: UserDTO,
    ) -> OrganizationRequestDTO:
        async with self.uow as uow:
            request = await self._get_by_id_or_raise(uow.session, request_id)
            self._ensure_pending(request)

            await self.repository.update(
                uow.session,
                request.id,
                {
                    "status": OrganizationRequestStatus.REJECTED,
                    "reviewed_by_id": admin.id,
                    "reviewed_at": self._now(),
                    "reject_reason": data.reject_reason,
                },
            )
            await uow.commit()
            updated_request = await self._get_by_id_or_raise(uow.session, request.id)
            return OrganizationRequestDTO.model_validate(updated_request)

    async def _get_by_id_or_raise(
        self,
        session: AsyncSession,
        request_id: UUID,
    ):
        request = await self.repository.get_out(session, {"id": request_id})
        if not request:
            raise OrganizationRequestNotFoundError()
        return request

    def _ensure_pending(self, request: OrganizationRequest) -> None:
        if request.status != OrganizationRequestStatus.PENDING:
            raise OrganizationRequestStatusError()

    async def _ensure_organization_name_is_unique(
        self,
        session: AsyncSession,
        name: str,
    ) -> None:
        existing = await self.organization_repository.get(session, {"name": name})
        if existing:
            raise OrganizationAlreadyExistsError()

    def _now(self) -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)
