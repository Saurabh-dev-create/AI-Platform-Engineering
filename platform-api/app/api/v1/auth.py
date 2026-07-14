from fastapi import APIRouter, Depends

from app.auth.dependencies import (
    AuthenticatedIdentity,
    get_authenticated_identity,
)
from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
)
from app.schemas.auth import (
    AuthenticatedIdentityResponse,
    TokenResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/foundation-token",
    response_model=TokenResponse,
)
def create_foundation_token() -> TokenResponse:
    """
    Issue temporary foundation tokens for authentication verification.

    This endpoint will be removed when database-backed user login
    is implemented.
    """

    foundation_user_id = "foundation-user"

    return TokenResponse(
        access_token=create_access_token(
            subject=foundation_user_id,
        ),
        refresh_token=create_refresh_token(
            subject=foundation_user_id,
        ),
    )


@router.get(
    "/identity",
    response_model=AuthenticatedIdentityResponse,
)
def read_authenticated_identity(
    identity: AuthenticatedIdentity = Depends(
        get_authenticated_identity
    ),
) -> AuthenticatedIdentityResponse:
    """
    Return the identity extracted from a valid access token.
    """

    return AuthenticatedIdentityResponse(
        user_id=identity.user_id,
        token_id=identity.token_id,
    )
