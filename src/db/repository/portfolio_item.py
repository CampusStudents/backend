from sqlalchemy import Select
from sqlalchemy.orm import joinedload

from src.db.models import PortfolioItem
from src.db.repository.base import SQLAlchemyRepository


class PortfolioItemRepository(SQLAlchemyRepository):
    model = PortfolioItem

    def apply_related_load(
        self,
        query: Select[tuple[PortfolioItem]],
    ) -> Select[tuple[PortfolioItem]]:
        return query.options(joinedload(PortfolioItem.team_role))
