from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """
    Runtime configuration for the deployment controller.
    """

    app_name: str = Field(
        default="Zevinq Deployment Controller",
        validation_alias="DEPLOYMENT_CONTROLLER_APP_NAME",
    )

    log_level: str = Field(
        default="INFO",
        validation_alias="LOG_LEVEL",
    )

    postgres_host: str = Field(
        default="postgres",
        validation_alias="POSTGRES_HOST",
    )

    postgres_port: int = Field(
        default=5432,
        validation_alias="POSTGRES_PORT",
    )

    postgres_db: str = Field(
        default="ai_platform",
        validation_alias="POSTGRES_DB",
    )

    postgres_user: str = Field(
        default="ai_platform",
        validation_alias="POSTGRES_USER",
    )

    postgres_password: str = Field(
        validation_alias="POSTGRES_PASSWORD",
    )

    poll_interval_seconds: int = Field(
        default=5,
        ge=1,
        validation_alias=(
            "DEPLOYMENT_CONTROLLER_POLL_INTERVAL_SECONDS"
        ),
    )

    batch_size: int = Field(
        default=20,
        ge=1,
        le=100,
        validation_alias=(
            "DEPLOYMENT_CONTROLLER_BATCH_SIZE"
        ),
    )

    stale_after_seconds: int = Field(
        default=300,
        ge=30,
        validation_alias=(
            "DEPLOYMENT_CONTROLLER_STALE_AFTER_SECONDS"
        ),
    )

    runtime: str = Field(
        default="simulated",
        validation_alias="DEPLOYMENT_RUNTIME",
    )

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            "postgresql+psycopg://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
