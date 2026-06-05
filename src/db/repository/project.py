from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.db.models import Project, ProjectFavorite
from src.db.repository.base import SQLAlchemyRepository


class ProjectRepository(SQLAlchemyRepository):
    model = Project

    def apply_related_load(
        self,
        query: Select[tuple[Project]],
    ) -> Select[tuple[Project]]:
        return query.options(selectinload(Project.vacancies), joinedload(Project.event))

    async def get_favorites(
        self,
        session: AsyncSession,
        user_id: UUID,
        filters: dict | None,
    ) -> Sequence[Project]:
        stmt = (
            self.statement_get()
            .join(ProjectFavorite, ProjectFavorite.project_id == Project.id)
            .where(ProjectFavorite.user_id == user_id)
        )
        stmt = self.apply_filters(stmt, filters)
        stmt = self.apply_related_load(stmt)
        stmt = self.apply_pagination(stmt, filters)
        result = await session.scalars(stmt)
        return result.all()
