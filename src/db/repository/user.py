from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import Role, User
from src.db.models.rbac import user_roles
from src.db.repository.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User

    async def get_by_email_with_roles(
            self, session: AsyncSession, email: str
    ) -> User | None:
        stmt = (
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.email == email)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_roles(self, session: AsyncSession, user_id) -> User | None:
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
            .execution_options(populate_existing=True)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def assign_roles(
            self, session: AsyncSession, user_id, role_ids: list
    ) -> None:
        if not role_ids:
            return
        rows = [{"user_id": user_id, "role_id": role_id} for role_id in role_ids]
        stmt = insert(user_roles).values(rows).on_conflict_do_nothing()
        await session.execute(stmt)

    async def replace_roles(
            self, session: AsyncSession, user_id, role_ids: list
    ) -> None:
        await session.execute(delete(user_roles).where(user_roles.c.user_id == user_id))
        await self.assign_roles(session, user_id, role_ids)
