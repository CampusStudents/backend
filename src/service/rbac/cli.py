import asyncio
from logging import getLogger
from src.core.config import configure_logging
from src.db.db_helper import db_helper
from src.service.rbac.bootstrap import bootstrap_rbac

logger = getLogger(__name__)
async def run_bootstrap_rbac() -> None:
    async with db_helper.async_session_factory() as session:
        await bootstrap_rbac(session)
    await db_helper.dispose()
    logger.info("RBAC roles and permissions created successfully")



def main() -> None:
    configure_logging()
    asyncio.run(run_bootstrap_rbac())


if __name__ == "__main__":
    main()
