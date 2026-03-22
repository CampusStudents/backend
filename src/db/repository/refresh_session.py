from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from .base import SQLAlchemyRepository
from src.db.models import RefreshSession


class RefreshSessionRepository(SQLAlchemyRepository):
    model = RefreshSession

    async def delete_by_token(self, session: AsyncSession, token: str) -> None:
        await session.execute(
            delete(RefreshSession).where(RefreshSession.refresh_token == token)
        )

    async def delete_by_user_id(self, session: AsyncSession, user_id: UUID) -> None:
        await session.execute(
            delete(RefreshSession).where(RefreshSession.user_id == user_id)
        )
