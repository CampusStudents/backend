import asyncio
from logging import getLogger

from src.core.config import configure_logging
from src.db.db_helper import db_helper
from src.service.demo_seed.seed import bootstrap_demo_seed

logger = getLogger(__name__)


async def run_bootstrap_demo_seed() -> None:
    async with db_helper.async_session_factory() as session:
        await bootstrap_demo_seed(session)
    await db_helper.dispose()
    logger.info("Demo seed data created successfully")


def main() -> None:
    configure_logging()
    asyncio.run(run_bootstrap_demo_seed())


if __name__ == "__main__":
    main()
