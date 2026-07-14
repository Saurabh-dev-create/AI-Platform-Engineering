from dataclasses import dataclass

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt import (
    TokenValidationError,
    decode_token,
)
from app.core.exceptions import PlatformException


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


@dataclass(frozen=True)
class AuthenticatedIdentity:
    """
    Authenticated identity extracted from a valid access token.

    The database-backed current User model will be added when the
    Users schema and repository are implemented.
    """

    user_id: str
    token_id: str


def get_authenticated_identity(
    token: str = Depends(oauth2_scheme),
) -> AuthenticatedIdentity:
    """
    Validate the bearer access token and return its identity context.
    """

    try:
        payload = decode_token(
            token,
            expected_type="access",
        )

    except TokenValidationError as exc:
        raise PlatformException(
            message="Invalid or expired access token",
            error_code="AUTHENTICATION_FAILED",
            status_code=401,
        ) from exc

    return AuthenticatedIdentity(
        user_id=str(payload["sub"]),
        token_id=str(payload["jti"]),
    )
