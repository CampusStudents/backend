from fastapi import FastAPI
from fastapi.routing import APIRoute

from src.core.config import configure_logging
from src.web.api import api_router
from src.web.lifespan import lifespan_setup
from src.web.middleware import request_handler

OPENAPI_PREFIX_SEGMENTS = {"api", "v1"}


def generate_operation_id(route: APIRoute) -> str:
    path_segments = [
        segment
        for segment in route.path_format.strip("/").split("/")
        if segment and not segment.startswith("{")
    ]
    resource = next(
        (
            segment.replace("-", "_")
            for segment in path_segments
            if segment not in OPENAPI_PREFIX_SEGMENTS
        ),
        "root",
    )
    return f"{resource}-{route.name}"


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
        generate_unique_id_function=generate_operation_id,
    )

    # Add exception handler middleware
    app.middleware("http")(request_handler)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    return app
