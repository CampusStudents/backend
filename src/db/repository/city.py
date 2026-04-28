from src.db.models import City
from src.db.repository.base import SQLAlchemyRepository


class CityRepository(SQLAlchemyRepository):
    model = City
