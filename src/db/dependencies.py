from src.db.db_helper import db_helper
from src.db.repository.city import CityRepository
from src.db.repository.refresh_session import RefreshSessionRepository
from src.db.repository.role import RoleRepository
from src.db.repository.user import UserRepository
from src.db.unit_of_work import UnitOfWork


def get_unit_of_work() -> UnitOfWork:
    return UnitOfWork(db_helper.async_session_factory)


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_city_repository() -> CityRepository:
    return CityRepository()


def get_role_repository() -> RoleRepository:
    return RoleRepository()


def get_refresh_session_repository() -> RefreshSessionRepository:
    return RefreshSessionRepository()
