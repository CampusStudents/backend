from src.db.models import EventImageUrl, OrganizationImageUrl
from src.db.repository.base import SQLAlchemyRepository


class EventImageUrlRepository(SQLAlchemyRepository):
    model = EventImageUrl


class OrganizationImageUrlRepository(SQLAlchemyRepository):
    model = OrganizationImageUrl
