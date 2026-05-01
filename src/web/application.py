from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.core.config import configure_logging
from src.core.security.rate_limit import limiter
from src.web.api import api_router
from src.web.lifespan import lifespan_setup
from src.web.middleware import request_handler


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    configure_logging()
    app = FastAPI(
        title="campus",
        lifespan=lifespan_setup,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Add exception handler middleware
    app.middleware("http")(request_handler)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    return app
