from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config.logging import get_logger


logger = get_logger(__name__)


class PlatformException(Exception):
    """
    Base exception for expected AI Platform errors.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: str = "PLATFORM_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

        super().__init__(message)


class ResourceNotFoundException(PlatformException):
    """
    Raised when a platform resource does not exist.
    """

    def __init__(
        self,
        resource: str,
        resource_id: str,
    ) -> None:
        super().__init__(
            message=f"{resource} not found",
            error_code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={
                "resource": resource,
                "resource_id": resource_id,
            },
        )


class PolicyDeniedException(PlatformException):
    """
    Raised when platform governance denies an operation.
    """

    def __init__(
        self,
        message: str,
        *,
        policy: str | None = None,
    ) -> None:
        details = {}

        if policy:
            details["policy"] = policy

        super().__init__(
            message=message,
            error_code="POLICY_DENIED",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class QuotaExceededException(PlatformException):
    """
    Raised when a tenant or team exceeds an assigned quota.
    """

    def __init__(
        self,
        message: str,
        *,
        quota: str | None = None,
    ) -> None:
        details = {}

        if quota:
            details["quota"] = quota

        super().__init__(
            message=message,
            error_code="QUOTA_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details,
        )


class BudgetExceededException(PlatformException):
    """
    Raised when an AI usage or deployment budget is exceeded.
    """

    def __init__(
        self,
        message: str,
        *,
        budget_id: str | None = None,
    ) -> None:
        details = {}

        if budget_id:
            details["budget_id"] = budget_id

        super().__init__(
            message=message,
            error_code="BUDGET_EXCEEDED",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


def get_correlation_id(request: Request) -> str | None:
    """
    Return the request correlation ID when available.
    """

    return getattr(
        request.state,
        "correlation_id",
        None,
    )


async def platform_exception_handler(
    request: Request,
    exc: PlatformException,
) -> JSONResponse:
    correlation_id = get_correlation_id(request)

    logger.warning(
        "platform_request_rejected",
        error_code=exc.error_code,
        status_code=exc.status_code,
        path=request.url.path,
        details=exc.details,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "correlation_id": correlation_id,
            }
        },
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    correlation_id = get_correlation_id(request)

    logger.warning(
        "http_exception",
        status_code=exc.status_code,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
                "details": {},
                "correlation_id": correlation_id,
            }
        },
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    correlation_id = get_correlation_id(request)

    logger.warning(
        "request_validation_failed",
        path=request.url.path,
        validation_errors=exc.errors(),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {
                    "errors": exc.errors(),
                },
                "correlation_id": correlation_id,
            }
        },
    )


async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    correlation_id = get_correlation_id(request)

    logger.exception(
        "unexpected_platform_error",
        path=request.url.path,
        exception_type=type(exc).__name__,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_PLATFORM_ERROR",
                "message": "An unexpected platform error occurred",
                "details": {},
                "correlation_id": correlation_id,
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all Platform API exception handlers.
    """

    app.add_exception_handler(
        PlatformException,
        platform_exception_handler,
    )

    app.add_exception_handler(
        HTTPException,
        http_exception_handler,
    )

    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )

    app.add_exception_handler(
        Exception,
        unexpected_exception_handler,
    )
