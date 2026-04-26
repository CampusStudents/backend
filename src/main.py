import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.web.application import get_app

main_app = get_app()

main_app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=False,
    )
