from src.db.dependencies import (
    get_city_repository,
    get_refresh_session_repository,
    get_role_repository,
    get_unit_of_work,
    get_university_repository,
    get_user_profile_repository,
    get_user_repository,
)
from src.service.auth.service import AuthService
from src.service.city.service import CityService
from src.service.university.service import UniversityService
from src.service.user.service import UserService
from src.service.user_profile.service import UserProfileService


def get_auth_service() -> AuthService:
    return AuthService(
        get_unit_of_work(), get_refresh_session_repository(), get_user_repository()
    )


def get_user_service() -> UserService:
    return UserService(get_unit_of_work(), get_user_repository(), get_role_repository())


def get_city_service() -> CityService:
    return CityService(get_unit_of_work(), get_city_repository())


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
