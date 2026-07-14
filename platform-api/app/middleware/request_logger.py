from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config.logging import get_logger


logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Emit one structured log event for every completed HTTP request.

    Request metadata is enriched with correlation ID and processing
    duration captured by the upstream middleware layers.
    """

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        response = await call_next(request)

        correlation_id = getattr(
            request.state,
            "correlation_id",
            None,
        )

        duration_ms = getattr(
            request.state,
            "duration_ms",
            None,
        )

        logger.info(
            "http_request_completed",
            service="platform-api",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            correlation_id=correlation_id,
        )

        return response
