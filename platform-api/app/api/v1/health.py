from typing import Any

from fastapi import APIRouter, HTTPException, status
from redis import Redis
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config.logging import get_logger
from app.config.settings import settings
from app.database.connection import engine


router = APIRouter(tags=["Platform Health"])

logger = get_logger(__name__)


def check_postgres() -> bool:
    """
    Verify PostgreSQL connectivity.

    A lightweight SELECT statement is used because readiness checks
    should validate connectivity without performing expensive queries.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return True

    except SQLAlchemyError:
        logger.exception(
            "postgres_health_check_failed",
            component="postgres",
        )

        return False


def check_redis() -> bool:
    """
    Verify Redis connectivity using the Redis PING command.
    """

    redis_client = Redis.from_url(
        settings.redis_url,
        socket_connect_timeout=2,
        socket_timeout=2,
        decode_responses=True,
    )

    try:
        return bool(redis_client.ping())

    except Exception:
        logger.exception(
            "redis_health_check_failed",
            component="redis",
        )

        return False

    finally:
        redis_client.close()


@router.get("/live")
def liveness() -> dict[str, str]:
    """
    Kubernetes liveness probe.

    This endpoint only confirms that the Platform API process
    is running and capable of handling HTTP requests.
    """

    logger.info(
        "liveness_check_completed",
        service="platform-api",
    )

    return {
        "status": "alive",
        "service": "platform-api",
    }
    


@router.get("/ready")
def readiness() -> dict[str, str]:
    """
    Kubernetes readiness probe.

    The Platform API is considered ready only when its critical
    infrastructure dependencies are reachable.
    """

    postgres_healthy = check_postgres()
    redis_healthy = check_redis()

    if not postgres_healthy or not redis_healthy:
        logger.warning(
            "platform_api_not_ready",
            postgres=postgres_healthy,
            redis=redis_healthy,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Platform API dependencies are not ready",
        )

    return {
        "status": "ready",
        "service": "platform-api",
    }


@router.get("/health")
def health() -> dict[str, Any]:
    """
    Return detailed Platform API dependency health.
    """

    postgres_healthy = check_postgres()
    redis_healthy = check_redis()

    overall_status = (
        "healthy"
        if postgres_healthy and redis_healthy
        else "degraded"
    )

    response = {
        "status": overall_status,
        "service": "platform-api",
        "dependencies": {
            "postgres": {
                "status": (
                    "healthy"
                    if postgres_healthy
                    else "unhealthy"
                )
            },
            "redis": {
                "status": (
                    "healthy"
                    if redis_healthy
                    else "unhealthy"
                )
            },
        },
    }

    if overall_status == "degraded":
        logger.warning(
            "platform_health_degraded",
            postgres=postgres_healthy,
            redis=redis_healthy,
        )

    return response


@router.get("/version")
def version() -> dict[str, str]:
    """
    Return Platform API build and environment information.
    """

    return {
        "service": "platform-api",
        "version": settings.app_version,
        "environment": settings.app_env,
    }
   
