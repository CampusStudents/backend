from sqlalchemy import Select
from sqlalchemy.orm import joinedload, selectinload

from src.db.models import Organization
from src.db.repository.base import SQLAlchemyRepository


class OrganizationRepository(SQLAlchemyRepository):
    model = Organization

    def apply_related_load(
        self,
        query: Select[tuple[Organization]],
    ) -> Select[tuple[Organization]]:
        return query.options(
            joinedload(Organization.owner),
            selectinload(Organization.images),
        )
