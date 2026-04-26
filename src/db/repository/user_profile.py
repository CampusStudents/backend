from src.db.models import UserProfile
from src.db.repository.base import SQLAlchemyRepository


class UserProfileRepository(SQLAlchemyRepository):
    model = UserProfile
