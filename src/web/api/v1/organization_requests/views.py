from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Security, status

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.organization_request.schema import (
    CreateOrganizationRequestSchema,
    OrganizationRequestDTO,
    OrganizationRequestFilter,
    RejectOrganizationRequestSchema,
)
from src.service.user.schema import UserDTO
from src.web.api.dependencies import (
    OrganizationRequestServiceDep,
    get_current_active_user,
    get_current_active_user_with_profile,
)

router = APIRouter(prefix=settings.api.v1.organization_requests)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_organization_request(
    data: CreateOrganizationRequestSchema,
    service: OrganizationRequestServiceDep,
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.ORGANIZATION_REQUESTS_CREATE],
    ),
) -> OrganizationRequestDTO:
    return await service.create(data, user)


@router.get("/me")
async def get_my_organization_requests(
    service: OrganizationRequestServiceDep,
    user: UserDTO = Security(
        get_current_active_user,
        scopes=[Scope.ORGANIZATION_REQUESTS_LIST_OWN],
    ),
) -> list[OrganizationRequestDTO]:
    return await service.get_my_requests(user)


@router.get(
    "/",
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.ORGANIZATION_REQUESTS_LIST]),
    ],
)
async def get_organization_requests(
    service: OrganizationRequestServiceDep,
    filters: Annotated[OrganizationRequestFilter, Query()],
) -> list[OrganizationRequestDTO]:
    return await service.get_all(filters)


@router.patch("/{request_id}/approve")
async def approve_organization_request(
    request_id: UUID,
    service: OrganizationRequestServiceDep,
    admin: UserDTO = Security(
        get_current_active_user,
        scopes=[Scope.ORGANIZATION_REQUESTS_UPDATE],
    ),
) -> OrganizationRequestDTO:
    return await service.approve(request_id, admin)


@router.patch("/{request_id}/reject")
async def reject_organization_request(
    request_id: UUID,
    data: RejectOrganizationRequestSchema,
    service: OrganizationRequestServiceDep,
    admin: UserDTO = Security(
        get_current_active_user,
        scopes=[Scope.ORGANIZATION_REQUESTS_UPDATE],
    ),
) -> OrganizationRequestDTO:
    return await service.reject(request_id, data, admin)
