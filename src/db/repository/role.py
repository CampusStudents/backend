from src.db.models import Role
from src.db.repository.base import SQLAlchemyRepository


class RoleRepository(SQLAlchemyRepository):
    model = Role
