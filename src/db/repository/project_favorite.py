from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import ProjectFavorite


class ProjectFavoriteRepository:
    async def create_if_not_exists(
        self,
        session: AsyncSession,
        user_id: UUID,
        project_id: UUID,
    ) -> None:
        stmt = (
            insert(ProjectFavorite)
            .values(user_id=user_id, project_id=project_id)
            .on_conflict_do_nothing(
                index_elements=[
                    ProjectFavorite.user_id,
                    ProjectFavorite.project_id,
                ],
            )
        )
        await session.execute(stmt)

    async def delete(
        self,
        session: AsyncSession,
        user_id: UUID,
        project_id: UUID,
    ) -> None:
        stmt = delete(ProjectFavorite).where(
            ProjectFavorite.user_id == user_id,
            ProjectFavorite.project_id == project_id,
        )
        await session.execute(stmt)

    async def exists(
        self,
        session: AsyncSession,
        user_id: UUID,
        project_id: UUID,
    ) -> bool:
        stmt = select(ProjectFavorite.user_id).where(
            ProjectFavorite.user_id == user_id,
            ProjectFavorite.project_id == project_id,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_project_ids(
        self,
        session: AsyncSession,
        user_id: UUID,
        project_ids: list[UUID],
    ) -> set[UUID]:
        if not project_ids:
            return set()

        stmt = select(ProjectFavorite.project_id).where(
            ProjectFavorite.user_id == user_id,
            ProjectFavorite.project_id.in_(project_ids),
        )
        result = await session.scalars(stmt)
        return set(result.all())
