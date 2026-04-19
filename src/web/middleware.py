"""Exception handler middleware for FastAPI application."""

import logging
from uuid import uuid4

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse

from src.core.exceptions.api.base import InternalServerException
from src.core.exceptions.service.base import (
    AppError,
    AuthError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    InvalidInputError,
    NotFoundError,
)
from src.core.utils.helpers import get_time
from src.web.api.monitoring import router as monitoring_router

logger = logging.getLogger(__name__)

MONITORING_ROUTE_PATHS = {
    route.path for route in monitoring_router.routes if hasattr(route, "path")
}
MONITORING_ROUTE_PATHS.update([f"/api{path}" for path in MONITORING_ROUTE_PATHS])


async def request_handler(request: Request, call_next):
    """Middleware used by FastAPI to process each request"""

    # Skip logging for healthcheck endpoint
    is_healthcheck = request.url.path in MONITORING_ROUTE_PATHS

    start_time = get_time(seconds_precision=False)
    request_id = str(uuid4())

    if not is_healthcheck:
        logger.debug(
            "Request started: request_id=%s method=%s url=%s",
            request_id,
            request.method,
            str(request.url),
        )

    try:
        response: Response = await call_next(request)

    except AppError as exc:
        response = ErrorProcessor.process_app_exception(exc)

    except HTTPException as exc:
        response = ErrorProcessor.process_http_exception(exc)

    except Exception:
        logger.exception("Unexpected error: request_id=%s", request_id)
        response = InternalServerException().response()

    end_time = get_time(seconds_precision=False)
    time_elapsed = round(end_time - start_time, 5)

    if not is_healthcheck:
        logger.debug(
            "Request ended: request_id=%s status=%s time_elapsed=%s",
            request_id,
            response.status_code,
            time_elapsed,
        )

    return response


class ErrorProcessor:
    """Process and log different types of exceptions."""

    @classmethod
    def log_exception(cls, exc: Exception, status_code: int) -> None:
        """Log exception based on status code."""
        if status_code < 500: # noqa: PLR2004
            logger.info("Client-side error: status=%s error=%s", status_code, str(exc))
        else:
            logger.warning(
                "Server-side error: status=%s error=%s", status_code, str(exc)
            )

    @classmethod
    def process_app_exception(cls, exc: AppError) -> JSONResponse:
        """Process custom application exceptions."""
        special_message = None
        if isinstance(exc, ForbiddenError):
            status_code = 403
        elif isinstance(exc, NotFoundError):
            status_code = 404
        elif isinstance(exc, ConflictError):
            status_code = 409
        elif isinstance(exc, AuthError):
            status_code = 401
        elif isinstance(exc, InvalidInputError):
            status_code = 422
        elif isinstance(exc, BadRequestError):
            status_code = 400
        else:
            status_code = 400

        cls.log_exception(exc, status_code)
        return JSONResponse(
            status_code=status_code,
            content={"detail": special_message if special_message else exc.detail},
        )

    @classmethod
    def process_http_exception(cls, exc: HTTPException) -> JSONResponse:
        """Process FastAPI HTTPException."""
        status_code = exc.status_code
        detail = exc.detail
        cls.log_exception(exc, status_code)
        return JSONResponse(status_code=status_code, content={"detail": detail})
