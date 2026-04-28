from src.db.models import Skill
from src.db.repository.base import SQLAlchemyRepository


class SkillRepository(SQLAlchemyRepository):
    model = Skill
