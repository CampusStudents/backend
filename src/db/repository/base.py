from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import Select, delete, insert, inspect, select, update
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.db.models import Base


class SQLAlchemyRepository[Model: Base]:
    model: type[Model]

    def _filter_model_fields(self, data: dict) -> dict:
        mapper = inspect(self.model)
        return {k: v for k, v in data.items() if k in mapper.columns}

    def statement_get(self) -> Select[tuple[Model]]:
        return select(self.model)

    def apply_related_load(
        self,
        query: Select[tuple[Model]],
    ) -> Select[tuple[Model]]:
        return query

    def apply_filters(
        self,
        query: Select[tuple[Model]],
        filters: dict | None = None,
    ) -> Select[tuple[Model]]:
        if not filters:
            return query

        mapper = inspect(self.model)
        for key, value in filters.items():
            if key not in mapper.columns:
                msg = f"Unknown filter field '{key}' for {self.model.__name__}"
                raise ValueError(msg)

            column = getattr(self.model, key)
            if isinstance(value, list | tuple | set | frozenset):
                query = query.where(column.in_(value))
            elif value is None:
                query = query.where(column.is_(None))
            else:
                query = query.where(column == value)
        return query

    def apply_order_by(
        self,
        stmt: Select[tuple[Model]],
        order_by: tuple[Any, ...] | None = None,
    ) -> Select[tuple[Model]]:
        if order_by is None:
            return stmt
        return stmt.order_by(*order_by)

    async def create(self, session: AsyncSession, data: dict) -> Model:
        data_to_create = self._filter_model_fields(data)
        stmt = insert(self.model).values(**data_to_create).returning(self.model)
        result = await session.execute(stmt)
        return result.scalar()

    async def get(
        self,
        session: AsyncSession,
        filters: dict,
    ) -> Model | None:
        stmt = self.statement_get()
        stmt = self.apply_filters(stmt, filters)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_out(
        self,
        session: AsyncSession,
        filters: dict,
    ) -> Model | None:
        stmt = self.statement_get()
        stmt = self.apply_filters(stmt, filters)
        stmt = self.apply_related_load(stmt)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        session: AsyncSession,
        filters: dict | None = None,
        order_by: tuple[Any, ...] | None = None,
    ) -> Sequence[Model]:
        stmt = self.statement_get()
        stmt = self.apply_filters(stmt, filters)
        stmt = self.apply_order_by(stmt, order_by)
        result = await session.scalars(stmt)
        return result.all()

    async def get_multi_out(
        self,
        session: AsyncSession,
        filters: dict | None = None,
        order_by: tuple[Any, ...] | None = None,
    ) -> Sequence[Model]:
        stmt = self.statement_get()
        stmt = self.apply_filters(stmt, filters)
        stmt = self.apply_related_load(stmt)
        stmt = self.apply_order_by(stmt, order_by)
        result = await session.scalars(stmt)
        return result.all()

    async def delete_by_id(self, session: AsyncSession, entity_id: UUID) -> None:
        await session.execute(delete(self.model).where(self.model.id == entity_id))

    async def update(
            self, session: AsyncSession, entity_id: UUID, data: dict
    ) -> Model | None:
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
