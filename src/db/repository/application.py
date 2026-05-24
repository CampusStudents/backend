from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.choices import ApplicationStatus
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

    async def count_by_vacancy_status(
        self,
        session: AsyncSession,
        vacancy_id: UUID,
        status: ApplicationStatus,
    ) -> int:
        result = await session.execute(
            select(func.count(Application.id)).where(
                Application.vacancy_id == vacancy_id,
                Application.status == status,
            )
        )
        return result.scalar_one()
