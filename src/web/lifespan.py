from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.db.db_helper import db_helper
from src.service.rbac.bootstrap import bootstrap_rbac


@asynccontextmanager
async def lifespan_setup(
        app: FastAPI, # noqa: ARG001
) -> AsyncGenerator[None]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :return: function that actually performs actions.
    """

    # Init integrations (DB, Broker, etc...)
    async with db_helper.async_session_factory() as session:
        await bootstrap_rbac(session)

    yield
    # Close connections
    await db_helper.dispose()
