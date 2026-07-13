from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.config.logging import configure_logging, get_logger
from app.config.settings import settings


configure_logging()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage Platform API lifecycle events.
    """

    logger.info(
        "application_started",
        service="platform-api",
        environment=settings.app_env,
        version=settings.app_version,
    )

    yield

    logger.info(
        "application_stopped",
        service="platform-api",
        environment=settings.app_env,
    )


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Self-service AI Platform API for deploying, managing, "
        "observing, securing, and scaling AI agents."
    ),
    debug=settings.debug,
    lifespan=lifespan,
)


app.include_router(api_router)


@app.get("/", tags=["Platform"])
def platform_root() -> dict[str, str]:
    """
    Return basic Platform API information.
    """

    return {
        "service": "platform-api",
        "platform": "AI Agent Platform",
        "status": "running",
        "version": settings.app_version,
    }
