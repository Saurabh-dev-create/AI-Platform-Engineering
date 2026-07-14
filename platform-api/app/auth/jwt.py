from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import uuid4

import jwt
from jwt import InvalidTokenError

from app.config.settings import settings


TokenType = Literal["access", "refresh"]

TOKEN_ISSUER = "ai-agent-platform"
TOKEN_AUDIENCE = "platform-api"


class TokenValidationError(Exception):
    """
    Raised when a JWT cannot be trusted or validated.
    """


def _create_token(
    *,
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a signed JWT for an authenticated platform identity.
    """

    now = datetime.now(UTC)

    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "nbf": now,
        "exp": now + expires_delta,
        "iss": TOKEN_ISSUER,
        "aud": TOKEN_AUDIENCE,
        "jti": str(uuid4()),
    }

    if additional_claims:
        protected_claims = {
            "sub",
            "type",
            "iat",
            "nbf",
            "exp",
            "iss",
            "aud",
            "jti",
        }

        if protected_claims.intersection(additional_claims):
            raise ValueError(
                "Additional claims cannot override protected JWT claims"
            )

        payload.update(additional_claims)

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(
    *,
    subject: str,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a short-lived access token.
    """

    return _create_token(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(
            minutes=settings.jwt_access_token_expire_minutes,
        ),
        additional_claims=additional_claims,
    )


def create_refresh_token(
    *,
    subject: str,
) -> str:
    """
    Create a longer-lived refresh token.
    """

    return _create_token(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(
            days=settings.jwt_refresh_token_expire_days,
        ),
    )


def decode_token(
    token: str,
    *,
    expected_type: TokenType,
) -> dict[str, Any]:
    """
    Validate and decode a signed platform JWT.
    """

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            audience=TOKEN_AUDIENCE,
            issuer=TOKEN_ISSUER,
            options={
                "require": [
                    "sub",
                    "type",
                    "iat",
                    "nbf",
                    "exp",
                    "iss",
                    "aud",
                    "jti",
                ]
            },
        )

    except InvalidTokenError as exc:
        raise TokenValidationError(
            "Token validation failed"
        ) from exc

    if payload.get("type") != expected_type:
        raise TokenValidationError(
            f"Expected {expected_type} token"
        )

    return payload
