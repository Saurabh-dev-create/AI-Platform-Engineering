from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Attach a correlation ID to every incoming HTTP request.

    If the caller already provides an X-Correlation-ID header,
    the same value is reused.

    Otherwise, the Platform API generates a new UUID.

    The correlation ID is:
    - stored on request.state
    - bound to the structured logging context
    - returned in the HTTP response header
    """

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        correlation_id = (
            request.headers.get(CORRELATION_ID_HEADER)
            or str(uuid4())
        )

        request.state.correlation_id = correlation_id

        structlog.contextvars.clear_contextvars()

        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
        )

        try:
            response = await call_next(request)

            response.headers[CORRELATION_ID_HEADER] = correlation_id

            return response

        finally:
            structlog.contextvars.clear_contextvars()
