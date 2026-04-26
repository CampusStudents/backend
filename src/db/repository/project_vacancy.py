from uuid import UUID

from sqlalchemy import Select, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import ProjectVacancy, project_vacancy_skills
from src.db.repository.base import SQLAlchemyRepository


class ProjectVacancyRepository(SQLAlchemyRepository):
    model = ProjectVacancy

    def apply_related_load(
        self,
        query: Select[tuple[ProjectVacancy]],
    ) -> Select[tuple[ProjectVacancy]]:
        return query.options(selectinload(ProjectVacancy.skills))

    async def set_skills(
        self,
        session: AsyncSession,
        vacancy_id: UUID,
        skill_ids: list[UUID],
    ) -> None:
        await session.execute(
            delete(project_vacancy_skills).where(
                project_vacancy_skills.c.vacancy_id == vacancy_id
            )
        )
        if not skill_ids:
            return
        await session.execute(
            insert(project_vacancy_skills),
            [
                {"vacancy_id": vacancy_id, "skill_id": skill_id}
                for skill_id in skill_ids
            ],
        )
