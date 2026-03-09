from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.db.models import db_helper


@asynccontextmanager
async def lifespan_setup(app: FastAPI) -> AsyncGenerator[None, None]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :return: function that actually performs actions.
    """

    # Init integrations (DB, Broker, etc...)

    yield
    # Close connections
    await db_helper.dispose()
