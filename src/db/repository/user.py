from uuid import UUID

from sqlalchemy import Select, delete, insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import Role, User, user_skills
from src.db.models.rbac import user_roles
from src.db.repository.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User

    def apply_related_load(
        self,
        query: Select[tuple[User]],
    ) -> Select[tuple[User]]:
        return query.options(selectinload(User.roles).selectinload(Role.permissions))

    async def assign_roles(
        self, session: AsyncSession, user_id, role_ids: list
    ) -> None:
        if not role_ids:
            return
        rows = [{"user_id": user_id, "role_id": role_id} for role_id in role_ids]
        stmt = pg_insert(user_roles).values(rows).on_conflict_do_nothing()
        await session.execute(stmt)

    async def replace_roles(
        self, session: AsyncSession, user_id, role_ids: list
    ) -> None:
        await session.execute(delete(user_roles).where(user_roles.c.user_id == user_id))
        await self.assign_roles(session, user_id, role_ids)

    async def get_with_skills(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> User | None:
        stmt = select(User).options(selectinload(User.skills)).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def replace_skills(
        self,
        session: AsyncSession,
        user_id: UUID,
        skill_ids: list[UUID],
    ) -> None:
        await session.execute(
            delete(user_skills).where(user_skills.c.user_id == user_id)
        )
        if not skill_ids:
            return
        await session.execute(
            insert(user_skills),
            [{"user_id": user_id, "skill_id": skill_id} for skill_id in skill_ids],
        )
