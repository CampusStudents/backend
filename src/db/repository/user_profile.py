from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import UserProfile
from src.db.repository.base import SQLAlchemyRepository


class UserProfileRepository(SQLAlchemyRepository):
    model = UserProfile

    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> UserProfile | None:
        result = await session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
