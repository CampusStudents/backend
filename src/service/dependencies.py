from src.db.dependencies import (
    get_application_repository,
    get_city_repository,
    get_event_image_url_repository,
    get_event_repository,
    get_organization_image_url_repository,
    get_organization_repository,
    get_organization_request_repository,
    get_portfolio_item_repository,
    get_project_repository,
    get_project_vacancy_repository,
    get_refresh_session_repository,
    get_role_repository,
    get_skill_repository,
    get_team_member_repository,
    get_team_role_repository,
    get_unit_of_work,
    get_university_repository,
    get_user_profile_repository,
    get_user_repository,
)
from src.service.application.service import ApplicationService
from src.service.auth.service import AuthService
from src.service.city.service import CityService
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
from src.service.user.service import UserService
from src.service.user_profile.service import UserProfileService


def get_auth_service() -> AuthService:
    return AuthService(
        get_unit_of_work(), get_refresh_session_repository(), get_user_repository()
    )


def get_user_service() -> UserService:
    return UserService(get_unit_of_work(), get_user_repository(), get_role_repository())


def get_application_service() -> ApplicationService:
    return ApplicationService(
        get_unit_of_work(),
        get_application_repository(),
        get_project_repository(),
        get_project_vacancy_repository(),
        get_team_member_repository(),
    )


def get_city_service() -> CityService:
    return CityService(get_unit_of_work(), get_city_repository())


def get_event_service() -> EventService:
    return EventService(
        get_unit_of_work(),
        get_event_repository(),
        get_city_repository(),
        get_organization_repository(),
        get_event_image_url_repository(),
    )


def get_organization_request_service() -> OrganizationRequestService:
    return OrganizationRequestService(
        get_unit_of_work(),
        get_organization_request_repository(),
        get_organization_repository(),
        get_role_repository(),
        get_user_repository(),
    )


def get_organization_service() -> OrganizationService:
    return OrganizationService(
        get_unit_of_work(),
        get_organization_repository(),
        get_user_repository(),
        get_role_repository(),
        get_organization_image_url_repository(),
    )


def get_portfolio_item_service() -> PortfolioItemService:
    return PortfolioItemService(
        get_unit_of_work(),
        get_portfolio_item_repository(),
        get_user_repository(),
        get_team_role_repository(),
        get_skill_repository(),
    )


def get_skill_service() -> SkillService:
    return SkillService(get_unit_of_work(), get_skill_repository())


def get_team_role_service() -> TeamRoleService:
    return TeamRoleService(get_unit_of_work(), get_team_role_repository())


def get_team_member_service() -> TeamMemberService:
    return TeamMemberService(
        get_unit_of_work(),
        get_team_member_repository(),
        get_project_repository(),
    )


def get_project_service() -> ProjectService:
    return ProjectService(
        get_unit_of_work(),
        get_project_repository(),
        get_city_repository(),
        get_event_repository(),
        get_application_repository(),
    )


def get_project_vacancy_service() -> ProjectVacancyService:
    return ProjectVacancyService(
        get_unit_of_work(),
        get_project_vacancy_repository(),
        get_project_repository(),
        get_team_role_repository(),
        get_skill_repository(),
    )


def get_recommendation_service() -> RecommendationService:
    return RecommendationService(
        get_unit_of_work(),
        get_project_vacancy_repository(),
        get_user_repository(),
    )


def get_university_service() -> UniversityService:
    return UniversityService(
        get_unit_of_work(),
        get_university_repository(),
        get_city_repository(),
    )


def get_user_profile_service() -> UserProfileService:
    return UserProfileService(
        get_unit_of_work(),
        get_user_profile_repository(),
        get_user_repository(),
        get_city_repository(),
        get_university_repository(),
    )
