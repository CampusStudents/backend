from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes

from src.core.exceptions.service.auth import InvalidTokenError
from src.core.exceptions.service.base import ForbiddenError
from src.core.security.utils import decode_jwt
from src.service.application.service import ApplicationService
from src.service.auth.service import AuthService
from src.service.city.service import CityService
from src.service.dependencies import (
    get_application_service,
    get_auth_service,
    get_city_service,
    get_event_service,
    get_organization_request_service,
    get_organization_service,
    get_portfolio_item_service,
    get_project_service,
    get_project_vacancy_service,
    get_recommendation_service,
    get_skill_service,
    get_team_member_service,
    get_team_role_service,
    get_university_service,
    get_user_profile_service,
    get_user_service,
)
from src.service.event.service import EventService
from src.service.organization.service import OrganizationService
from src.service.organization_request.service import OrganizationRequestService
from src.service.portfolio_item.service import PortfolioItemService
from src.service.project.service import ProjectService
from src.service.project_vacancy.service import ProjectVacancyService
from src.service.recommendation.service import RecommendationService
from src.service.skill.service import SkillService
from src.service.team_member.service import TeamMemberService
from src.service.team_role.service import TeamRoleService
from src.service.university.service import UniversityService
from src.service.user.schema import UserDTO
from src.service.user.service import UserService
from src.service.user_profile.service import UserProfileService

http_bearer = HTTPBearer()

ApplicationServiceDep = Annotated[
    ApplicationService,
    Depends(get_application_service),
]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CityServiceDep = Annotated[CityService, Depends(get_city_service)]
EventServiceDep = Annotated[EventService, Depends(get_event_service)]
OrganizationServiceDep = Annotated[
    OrganizationService,
    Depends(get_organization_service),
]
OrganizationRequestServiceDep = Annotated[
    OrganizationRequestService,
    Depends(get_organization_request_service),
]
PortfolioItemServiceDep = Annotated[
    PortfolioItemService,
    Depends(get_portfolio_item_service),
]
SkillServiceDep = Annotated[SkillService, Depends(get_skill_service)]
TeamMemberServiceDep = Annotated[TeamMemberService, Depends(get_team_member_service)]
TeamRoleServiceDep = Annotated[TeamRoleService, Depends(get_team_role_service)]
ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
ProjectVacancyServiceDep = Annotated[
    ProjectVacancyService,
    Depends(get_project_vacancy_service),
]
RecommendationServiceDep = Annotated[
    RecommendationService,
    Depends(get_recommendation_service),
]
UniversityServiceDep = Annotated[UniversityService, Depends(get_university_service)]
UserProfileServiceDep = Annotated[
    UserProfileService,
    Depends(get_user_profile_service),
]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    token = credentials.credentials
    payload = decode_jwt(token)
    return payload


async def get_token_for_refresh(
    request: Request,
) -> str:
    token = request.cookies.get("refresh_token")
    if token:
        return token
    msg = "No token"
    raise InvalidTokenError(msg)


async def get_current_user(
    security_scopes: SecurityScopes,
    service: AuthServiceDep,
    payload: dict = Depends(get_current_token_payload),
) -> UserDTO:
    user = await service.get_current_user(payload)
    user_scopes = user.scopes
    for scope in security_scopes.scopes:
        if scope not in user_scopes and "*" not in user_scopes:
            msg = "Insufficient permissions"
            raise ForbiddenError(msg)
    return user


async def get_current_active_user(
    security_scopes: SecurityScopes,
    service: AuthServiceDep,
    payload: dict = Depends(get_current_token_payload),
) -> UserDTO:
    user = await get_current_user(security_scopes, service, payload)
    if not user.is_active:
        raise ForbiddenError(
            detail="User inactive",
        )
    return user


async def get_current_verified_user(
    security_scopes: SecurityScopes,
    service: AuthServiceDep,
    payload: dict = Depends(get_current_token_payload),
) -> UserDTO:
    user = await get_current_active_user(security_scopes, service, payload)
    if not user.is_verified:
        msg = "Email not verified. Please verify your email address."
        raise ForbiddenError(msg)
    return user


async def get_current_active_user_with_profile(
    security_scopes: SecurityScopes,
    service: AuthServiceDep,
    payload: dict = Depends(get_current_token_payload),
) -> UserDTO:
    user = await get_current_verified_user(security_scopes, service, payload)
    if not user.is_profile_completed:
        msg = (
            "Profile not completed. "
            "Please complete your profile at POST /api/v1/users/profile"
        )
        raise ForbiddenError(msg)
    return user
