from sqlalchemy import Select
from sqlalchemy.orm import selectinload

from src.db.models import Application, ProjectVacancy, User
from src.db.repository.base import SQLAlchemyRepository


class ApplicationRepository(SQLAlchemyRepository):
    model = Application

    def apply_related_load(
        self,
        query: Select[tuple[Application]],
    ) -> Select[tuple[Application]]:
        return query.options(
            selectinload(Application.applicant).selectinload(User.profile),
            selectinload(Application.vacancy).selectinload(ProjectVacancy.project),
            selectinload(Application.vacancy).selectinload(ProjectVacancy.team_role),
        )
