from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.jwt import (
    TokenValidationError,
    decode_token,
)
from app.core.exceptions import (
    InactiveUserException,
    PlatformException,
)
from app.dependencies.database import get_db_session
from app.models.user import User
from app.repositories.user_repository import UserRepository


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
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_session),
) -> User:
    """
    Validate an access token and return the real active platform user.
    """

    try:
        payload = decode_token(
            token,
            expected_type="access",
        )

        user_id = UUID(str(payload["sub"]))

    except (
        TokenValidationError,
        ValueError,
        TypeError,
    ) as exc:
        raise PlatformException(
            message="Invalid or expired access token",
            error_code="AUTHENTICATION_FAILED",
            status_code=401,
        ) from exc

    repository = UserRepository()

    user = repository.get_by_id(
        db,
        user_id,
    )

    if user is None:
        raise PlatformException(
            message="Invalid or expired access token",
            error_code="AUTHENTICATION_FAILED",
            status_code=401,
        )

    if not user.is_active:
        raise InactiveUserException()

    return user    
