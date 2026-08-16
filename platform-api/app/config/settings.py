from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration contract for the Platform API.

    Configuration is loaded from environment variables and the repository
    root .env file during local development.

    In Kubernetes, the same configuration keys will later be injected
    through ConfigMaps and Secrets.
    """

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = Field(
        default="AI Agent Platform API",
        validation_alias="APP_NAME",
    )

    app_env: Literal[
        "development",
        "testing",
        "staging",
        "production",
    ] = Field(
        default="development",
        validation_alias="APP_ENV",
    )

    app_version: str = Field(
        default="0.1.0",
        validation_alias="APP_VERSION",
    )

    debug: bool = Field(
        default=False,
        validation_alias="DEBUG",
    )

    api_v1_prefix: str = Field(
        default="/api/v1",
        validation_alias="API_V1_PREFIX",
    )

    host: str = Field(
        default="0.0.0.0",
        validation_alias="HOST",
    )

    port: int = Field(
        default=8000,
        validation_alias="PORT",
    )

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = Field(
        default="INFO",
        validation_alias="LOG_LEVEL",
    )

    log_format: Literal[
        "json",
        "console",
    ] = Field(
        default="json",
        validation_alias="LOG_FORMAT",
    )

    # ------------------------------------------------------------------
    # PostgreSQL
    # ------------------------------------------------------------------

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

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------

    redis_host: str = Field(
        default="redis",
        validation_alias="REDIS_HOST",
    )

    redis_port: int = Field(
        default=6379,
        validation_alias="REDIS_PORT",
    )

    redis_db: int = Field(
        default=0,
        validation_alias="REDIS_DB",
    )

    redis_password: str | None = Field(
        default=None,
        validation_alias="REDIS_PASSWORD",
    )

    @computed_field
    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return (
                f"redis://:{self.redis_password}@"
                f"{self.redis_host}:"
                f"{self.redis_port}/"
                f"{self.redis_db}"
            )

        return (
            f"redis://"
            f"{self.redis_host}:"
            f"{self.redis_port}/"
            f"{self.redis_db}"
        )

    # ------------------------------------------------------------------
    # JWT Authentication
    # ------------------------------------------------------------------

    jwt_secret_key: str = Field(
        min_length=32,
        validation_alias="JWT_SECRET_KEY",
    )

    jwt_algorithm: str = Field(
        default="HS256",
        validation_alias="JWT_ALGORITHM",
    )

    jwt_access_token_expire_minutes: int = Field(
        default=30,
        gt=0,
        validation_alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    jwt_refresh_token_expire_days: int = Field(
        default=7,
        gt=0,
        validation_alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS",
    )

    # ------------------------------------------------------------------
    # External Authentication / OAuth
    # ------------------------------------------------------------------

    google_oauth_client_id: str | None = Field(
        default=None,
        validation_alias="GOOGLE_OAUTH_CLIENT_ID",
    )

    google_oauth_client_secret: str | None = Field(
        default=None,
        validation_alias="GOOGLE_OAUTH_CLIENT_SECRET",
    )

    google_oauth_redirect_uri: str | None = Field(
        default=None,
        validation_alias="GOOGLE_OAUTH_REDIRECT_URI",
    )

    oauth_state_ttl_seconds: int = Field(
        default=600,
        ge=60,
        le=1800,
        validation_alias="OAUTH_STATE_TTL_SECONDS",
    )

    oauth_frontend_success_url: str = Field(
        default="http://localhost:5173/auth/callback",
        validation_alias="OAUTH_FRONTEND_SUCCESS_URL",
    )

    oauth_frontend_error_url: str = Field(
        default="http://localhost:5173/login",
        validation_alias="OAUTH_FRONTEND_ERROR_URL",
    )

    # ------------------------------------------------------------------
    # Platform Security
    # ------------------------------------------------------------------

    password_min_length: int = Field(
        default=12,
        ge=8,
        validation_alias="PASSWORD_MIN_LENGTH",
    )

    # ------------------------------------------------------------------
    # Internal Platform Services
    # ------------------------------------------------------------------

    ai_gateway_url: str = Field(
        default="http://ai-gateway:8080",
        validation_alias="AI_GATEWAY_URL",
    )

    ai_control_plane_url: str = Field(
        default="http://ai-control-plane:8081",
        validation_alias="AI_CONTROL_PLANE_URL",
    )

    deployment_controller_url: str = Field(
        default="http://deployment-controller:8082",
        validation_alias="DEPLOYMENT_CONTROLLER_URL",
    )

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------

    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        validation_alias="CORS_ORIGINS",
    )

    # ------------------------------------------------------------------
    # Future AI Provider Configuration
    # ------------------------------------------------------------------

    openai_api_key: str | None = Field(
        default=None,
        validation_alias="OPENAI_API_KEY",
    )

    aws_region: str = Field(
        default="ap-south-1",
        validation_alias="AWS_REGION",
    )

    # ------------------------------------------------------------------
    # Pydantic Settings Configuration
    # ------------------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    A single configuration object is shared by the application process.
    """

    return Settings()


settings = get_settings()
