from src.db.models import User
from src.db.repository.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User
