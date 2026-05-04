from uuid import UUID

from fastapi import APIRouter, Security

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.application.schema import ApplicationDTO
from src.service.user.schema import UserDTO
from src.web.api.dependencies import (
    ApplicationServiceDep,
    get_current_active_user,
)

router = APIRouter(prefix=settings.api.v1.applications)


@router.get("/me")
async def get_my_applications(
    service: ApplicationServiceDep,
    user: UserDTO = Security(
        get_current_active_user,
        scopes=[Scope.APPLICATIONS_LIST],
    ),
) -> list[ApplicationDTO]:
    return await service.get_my_applications(user)


@router.patch("/{application_id}/withdraw")
async def withdraw_application(
    application_id: UUID,
    service: ApplicationServiceDep,
    user: UserDTO = Security(
        get_current_active_user,
        scopes=[Scope.APPLICATIONS_WITHDRAW],
    ),
) -> ApplicationDTO:
    return await service.withdraw(application_id, user)
