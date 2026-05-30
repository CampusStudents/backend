from sqlalchemy import Select
from sqlalchemy.orm import joinedload

from src.db.models import OrganizationRequest
from src.db.repository.base import SQLAlchemyRepository


class OrganizationRequestRepository(SQLAlchemyRepository):
    model = OrganizationRequest

    def apply_related_load(
        self,
        query: Select[tuple[OrganizationRequest]],
    ) -> Select[tuple[OrganizationRequest]]:
        return query.options(
            joinedload(OrganizationRequest.user),
            joinedload(OrganizationRequest.reviewed_by),
        )
