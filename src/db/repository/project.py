from sqlalchemy import Select
from sqlalchemy.orm import selectinload

from src.db.models import Project
from src.db.repository.base import SQLAlchemyRepository


class ProjectRepository(SQLAlchemyRepository):
    model = Project

    def apply_related_load(
        self,
        query: Select[tuple[Project]],
    ) -> Select[tuple[Project]]:
        return query.options(selectinload(Project.vacancies))