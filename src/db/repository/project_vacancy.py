from uuid import UUID

from sqlalchemy import Select, delete, exists, insert, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.choices import ProjectStatus
from src.db.models import (
    Application,
    Project,
    ProjectVacancy,
    Skill,
    project_vacancy_skills,
)
from src.db.repository.base import SQLAlchemyRepository


class ProjectVacancyRepository(SQLAlchemyRepository):
    model = ProjectVacancy

    def apply_related_load(
        self,
        query: Select[tuple[ProjectVacancy]],
    ) -> Select[tuple[ProjectVacancy]]:
        return query.options(
            selectinload(ProjectVacancy.project),
            selectinload(ProjectVacancy.skills),
        )

    async def get_recommended_for_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        filters: dict,
    ) -> list[ProjectVacancy]:
        applied = exists().where(
            Application.vacancy_id == ProjectVacancy.id,
            Application.applicant_id == user_id,
        )
        query = (
            select(ProjectVacancy)
            .join(ProjectVacancy.project)
            .where(
                or_(Project.owner_id.is_(None), Project.owner_id != user_id),
                Project.status.notin_(
                    [ProjectStatus.ENDED, ProjectStatus.CANCELED],
                ),
                ~applied,
            )
            .options(
                selectinload(ProjectVacancy.project),
                selectinload(ProjectVacancy.skills),
            )
        )

        skill_id = filters.get("skill_id")
        team_role_id = filters.get("team_role_id")
        event_id = filters.get("event_id")
        city_id = filters.get("city_id")
        status = filters.get("status")
        format = filters.get("format")
        type = filters.get("type")
        if skill_id is not None:
            query = query.where(ProjectVacancy.skills.any(Skill.id == skill_id))
        if team_role_id is not None:
            query = query.where(ProjectVacancy.team_role_id == team_role_id)
        if event_id is not None:
            query = query.where(Project.event_id == event_id)
        if city_id is not None:
            query = query.where(Project.city_id == city_id)
        if status is not None:
            query = query.where(Project.status.in_(status))
        if format is not None:
            query = query.where(Project.format.in_(format))
        if type is not None:
            query = query.where(Project.type.in_(type))

        result = await session.scalars(query)
        return list(result.all())

    async def get_by_project_id(
        self,
        session: AsyncSession,
        project_id: UUID,
        filters: dict,
    ) -> list[ProjectVacancy]:
        query = (
            select(ProjectVacancy)
            .where(ProjectVacancy.project_id == project_id)
            .options(
                selectinload(ProjectVacancy.project),
                selectinload(ProjectVacancy.skills),
            )
        )
        skill_id = filters.get("skill_id")
        team_role_ids = filters.get("team_role_ids")
        if skill_id is not None:
            query = query.where(ProjectVacancy.skills.any(Skill.id == skill_id))
        if team_role_ids is not None:
            query = query.where(ProjectVacancy.team_role_id.in_(team_role_ids))
        offset = filters.get("offset", 0)
        limit = filters.get("limit")
        if offset:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        result = await session.scalars(query)
        return list(result.all())

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
