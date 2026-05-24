from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Security, status

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.organization.schema import (
    CreateOrganizationSchema,
    OrganizationDTO,
    OrganizationFilter,
    UpdateOrganizationSchema,
)
from src.web.api.dependencies import (
    OrganizationServiceDep,
    get_current_active_user,
)

router = APIRouter(prefix=settings.api.v1.organizations)


@router.get(
    "/",
    dependencies=[Security(get_current_active_user, scopes=[Scope.ORGANIZATIONS_LIST])],
)
async def get_organizations(
    service: OrganizationServiceDep,
    filters: Annotated[OrganizationFilter, Query()],
) -> list[OrganizationDTO]:
    return await service.get_all(filters)


@router.get(
    "/{organization_id}",
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.ORGANIZATIONS_DETAIL]),
    ],
)
async def get_organization(
    organization_id: UUID,
    service: OrganizationServiceDep,
) -> OrganizationDTO:
    return await service.get_by_id(organization_id)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.ORGANIZATIONS_CREATE]),
    ],
)
async def create_organization(
    data: CreateOrganizationSchema,
    service: OrganizationServiceDep,
) -> OrganizationDTO:
    return await service.create(data)


@router.patch(
    "/{organization_id}",
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.ORGANIZATIONS_UPDATE]),
    ],
)
async def update_organization(
    organization_id: UUID,
    data: UpdateOrganizationSchema,
    service: OrganizationServiceDep,
) -> OrganizationDTO:
    return await service.update(organization_id, data)


@router.delete(
    "/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Security(get_current_active_user, scopes=[Scope.ORGANIZATIONS_DELETE]),
    ],
)
async def delete_organization(
    organization_id: UUID,
    service: OrganizationServiceDep,
) -> None:
    await service.delete(organization_id)
