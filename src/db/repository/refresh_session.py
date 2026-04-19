from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import RefreshSession

from .base import SQLAlchemyRepository


class RefreshSessionRepository(SQLAlchemyRepository):
    model = RefreshSession

    async def delete_by_jti(self, session: AsyncSession, jti: str) -> None:
        await session.execute(
            delete(RefreshSession).where(RefreshSession.refresh_jti == jti)
        )

    async def delete_by_user_id(self, session: AsyncSession, user_id: UUID) -> None:
        await session.execute(
            delete(RefreshSession).where(RefreshSession.user_id == user_id)
        )
