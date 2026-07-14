from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


PROCESS_TIME_HEADER = "X-Process-Time-Ms"


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Measure HTTP request processing duration.

    The calculated duration is:

    - stored on request.state for downstream logging
    - returned in the X-Process-Time-Ms response header

    Prometheus and OpenTelemetry integrations will later use dedicated
    instrumentation for platform latency metrics and distributed traces.
    """

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        start_time = perf_counter()

        try:
            response = await call_next(request)

            return response

        finally:
            duration_ms = (perf_counter() - start_time) * 1000

            request.state.duration_ms = round(
                duration_ms,
                2,
            )

            if "response" in locals():
                response.headers[PROCESS_TIME_HEADER] = (
                    f"{request.state.duration_ms:.2f}"
                )
