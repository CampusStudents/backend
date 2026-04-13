from src.db.dependencies import (
    get_city_repository,
    get_unit_of_work,
    get_refresh_session_repository,
    get_user_repository,
    get_role_repository,
)
from src.service.auth.service import AuthService
from src.service.city.service import CityService
from src.service.user.service import UserService


def get_auth_service() -> AuthService:
    return AuthService(
        get_unit_of_work(), get_refresh_session_repository(), get_user_repository()
    )


def get_user_service() -> UserService:
    return UserService(get_unit_of_work(), get_user_repository(), get_role_repository())


def get_city_service() -> CityService:
    return CityService(get_unit_of_work(), get_city_repository())
