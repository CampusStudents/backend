import uvicorn

from src.core.config import settings
from src.web.application import get_app

main_app = get_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=False,
    )
