from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import insert, select, delete, inspect, update

from src.db.models import Base


class SQLAlchemyRepository[Model: Base]:
    model: type[Model]

    def _filter_model_fields(self, data: dict) -> dict:
        mapper = inspect(self.model)
        return {k: v for k, v in data.items() if k in mapper.columns}

    async def create(self, session: AsyncSession, data: dict) -> Model:
        data_to_create = self._filter_model_fields(data)
        stmt = insert(self.model).values(**data_to_create).returning(self.model)
        result = await session.execute(stmt)
        return result.scalar()

    async def get_all(self, session: AsyncSession) -> Sequence[Model]:
        result = await session.scalars(select(self.model))
        return result.all()

    async def get_by_filters(
            self, session: AsyncSession, filters: dict, one: bool = True
    ) -> Sequence[Model] | Model | None:
        stmt = select(self.model).filter_by(**filters)
        res = await session.execute(stmt)
        if one:
            return res.scalar_one_or_none()
        return res.scalars().all()

    async def delete_by_id(
            self, session: AsyncSession, entity_id: UUID
    ) -> None:
        await session.execute(delete(self.model).where(self.model.id == entity_id))

    async def get_by_id(self, session: AsyncSession, id: UUID) -> Model:
        return await session.get(self.model, id)

    async def update(self, session: AsyncSession, entity_id: UUID, data: dict) -> Model | None:
        data_to_update = self._filter_model_fields(data)
        if not data_to_update:
            return

        stmt = (
            update(self.model)
            .where(self.model.id == entity_id)
            .values(**data_to_update)
            .returning(self.model)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()