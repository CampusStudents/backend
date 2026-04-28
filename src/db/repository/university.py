from src.db.models import University
from src.db.repository.base import SQLAlchemyRepository


class UniversityRepository(SQLAlchemyRepository):
    model = University
