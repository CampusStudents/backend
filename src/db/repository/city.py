from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import City
from src.db.repository.base import SQLAlchemyRepository


class CityRepository(SQLAlchemyRepository):
    model = City

    async def get_by_name(self, session: AsyncSession, name: str) -> City | None:
        result = await session.execute(select(City).where(City.name == name))
        return result.scalar_one_or_none()
