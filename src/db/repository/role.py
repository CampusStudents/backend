from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Role
from src.db.repository.base import SQLAlchemyRepository


class RoleRepository(SQLAlchemyRepository):
    model = Role

    async def get_by_name(self, session: AsyncSession, name: str) -> Role | None:
        result = await session.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def get_by_names(
            self, session: AsyncSession, names: list[str]
    ) -> list[Role]:
        if not names:
            return []
        result = await session.execute(select(Role).where(Role.name.in_(names)))
        return list(result.scalars().all())
