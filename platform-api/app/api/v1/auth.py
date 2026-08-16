from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.clients.google_oauth_client import GoogleOAuthClient
from app.dependencies.database import get_db_session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.user_identity_repository import (
    UserIdentityRepository,
)
from app.repositories.team_entitlement_repository import (
    TeamEntitlementRepository,
)
from app.repositories.team_membership_repository import (
    TeamMembershipRepository,
)
from app.repositories.team_repository import TeamRepository
from app.schemas.auth import (
    LoginRequest,
    OAuthCallbackResponse,
    OAuthIdentityPreview,
    OAuthRegisterRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.entitlement_service import EntitlementService
from app.services.oauth_authentication_service import (
    OAuthAuthenticationService,
)
from app.services.oauth_pending_identity_service import (
    OAuthPendingIdentityService,
)
from app.services.oauth_onboarding_service import (
    OAuthOnboardingService,
)
from app.services.oauth_transaction_service import (
    OAuthTransactionService,
)
from app.services.self_service_onboarding_service import (
    SelfServiceOnboardingService,
)
from app.services.team_service import TeamService
from app.services.user_identity_service import (
    UserIdentityService,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get(
    "/oauth/google/start",
    response_class=RedirectResponse,
)
def start_google_login() -> RedirectResponse:
    google_client = GoogleOAuthClient()

    # Validate provider configuration before creating
    # short-lived OAuth state in Redis.
    google_client.ensure_configured()

    transaction_service = OAuthTransactionService()

    state, transaction = transaction_service.create(
        provider="google",
        mode="login",
    )

    authorization_url = (
        google_client.build_authorization_url(
            state=state,
            nonce=transaction.nonce,
            code_verifier=transaction.code_verifier,
        )
    )

    return RedirectResponse(
        url=authorization_url,
        status_code=307,
        headers={
            "Cache-Control": "no-store",
        },
    )


@router.get(
    "/oauth/google/callback",
    response_model=OAuthCallbackResponse,
)
def google_oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db_session),
) -> OAuthCallbackResponse:
    oauth_service = OAuthAuthenticationService()

    result = oauth_service.authenticate_google_callback(
        db,
        code=code,
        state=state,
    )

    if result.is_new_identity:
        pending_service = OAuthPendingIdentityService()

        continuation_token = pending_service.create(
            identity=result.external_identity,
        )

        return OAuthCallbackResponse(
            status="link_or_register_required",
            continuation_token=continuation_token,
            identity=OAuthIdentityPreview(
                provider=(
                    result.external_identity.provider
                ),
                email=result.external_identity.email,
                email_verified=(
                    result.external_identity.email_verified
                ),
                full_name=(
                    result.external_identity.full_name
                ),
                picture_url=(
                    result.external_identity.picture_url
                ),
            ),
        )

    if result.user is None:
        raise RuntimeError(
            "OAuth authentication returned no user"
        )

    auth_service = AuthService(
        UserRepository(),
    )

    tokens = auth_service.issue_tokens(
        user=result.user,
    )

    db.commit()

    return OAuthCallbackResponse(
        status="authenticated",
        tokens=tokens,
    )


@router.post(
    "/oauth/register",
    response_model=OAuthCallbackResponse,
)
def register_oauth_user(
    registration: OAuthRegisterRequest,
    db: Session = Depends(get_db_session),
) -> OAuthCallbackResponse:
    user_repository = UserRepository()

    entitlement_service = EntitlementService(
        TeamEntitlementRepository(),
    )

    team_service = TeamService(
        TeamRepository(),
        TeamMembershipRepository(),
        entitlement_service,
    )

    identity_service = UserIdentityService(
        UserIdentityRepository(),
    )

    onboarding_service = OAuthOnboardingService(
        user_repository=user_repository,
        pending_identity_service=(
            OAuthPendingIdentityService()
        ),
        identity_service=identity_service,
        team_service=team_service,
        entitlement_service=entitlement_service,
    )

    result = onboarding_service.register_free_user(
        db,
        continuation_token=(
            registration.continuation_token
        ),
    )

    auth_service = AuthService(
        user_repository,
    )

    tokens = auth_service.issue_tokens(
        user=result.user,
    )

    return OAuthCallbackResponse(
        status="authenticated",
        tokens=tokens,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register_user(
    registration: RegisterRequest,
    db: Session = Depends(get_db_session),
) -> UserResponse:
    entitlement_service = EntitlementService(
        TeamEntitlementRepository(),
    )

    auth_service = AuthService(
        UserRepository(),
    )

    team_service = TeamService(
        TeamRepository(),
        TeamMembershipRepository(),
        entitlement_service,
    )

    onboarding_service = SelfServiceOnboardingService(
        auth_service,
        team_service,
        entitlement_service,
    )

    user = onboarding_service.register_free_user(
        db,
        registration,
    )

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    login: LoginRequest,
    db: Session = Depends(get_db_session),
) -> TokenResponse:
    repository = UserRepository()
    service = AuthService(repository)

    return service.login_user(
        db,
        login,
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)
