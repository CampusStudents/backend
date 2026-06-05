from sqlalchemy import Select
from sqlalchemy.orm import joinedload, selectinload

from src.db.models import Event
from src.db.repository.base import SQLAlchemyRepository


class EventRepository(SQLAlchemyRepository):
    model = Event

    def apply_related_load(
        self,
        query: Select[tuple[Event]],
    ) -> Select[tuple[Event]]:
        return query.options(
            joinedload(Event.organizer),
            joinedload(Event.city),
            selectinload(Event.images),
        )
