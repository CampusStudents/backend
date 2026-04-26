from src.db.models import TeamRole
from src.db.repository.base import SQLAlchemyRepository


class TeamRoleRepository(SQLAlchemyRepository):
    model = TeamRole
