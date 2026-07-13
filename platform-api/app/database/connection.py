from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.config.logging import get_logger
from app.config.settings import settings


logger = get_logger(__name__)


def create_database_engine() -> Engine:
    """
    Create the SQLAlchemy engine used by the Platform API.

    The engine is configured for PostgreSQL and uses connection pool
    pre-ping so stale database connections can be detected before use.
    """

    logger.info(
        "database_engine_initializing",
        database_host=settings.postgres_host,
        database_port=settings.postgres_port,
        database_name=settings.postgres_db,
    )

    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )


engine = create_database_engine()
