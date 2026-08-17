from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.clients.google_oauth_client import GoogleOAuthClient
from app.config.settings import settings
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
    LinkedIdentityResponse,
    LoginRequest,
    OAuthCallbackResponse,
    OAuthHandoffRequest,
    OAuthHandoffResponse,
    OAuthIdentityPreview,
    OAuthRegisterRequest,
    OAuthStartResponse,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.entitlement_service import EntitlementService
from app.services.oauth_authentication_service import (
    OAuthAuthenticationService,
)
from app.services.oauth_browser_handoff_service import (
    OAuthBrowserHandoff,
    OAuthBrowserHandoffService,
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
    "/identities",
    response_model=list[LinkedIdentityResponse],
)
def list_linked_identities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[LinkedIdentityResponse]:
    identity_service = UserIdentityService(
        UserIdentityRepository(),
    )

    identities = identity_service.list_identities(
        db,
        user_id=current_user.id,
    )

    return [
        LinkedIdentityResponse(
            id=str(identity.id),
            provider=identity.provider,
            provider_email=identity.provider_email,
            provider_email_verified=(
                identity.provider_email_verified
            ),
            last_login_at=identity.last_login_at,
        )
        for identity in identities
    ]


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


@router.post(
    "/oauth/google/link/start",
    response_model=OAuthStartResponse,
)
def start_google_link(
    current_user: User = Depends(get_current_user),
) -> OAuthStartResponse:
    """
    Start an authenticated Google account-linking transaction.

    The initiating Zevinq user is bound server-side to the
    short-lived OAuth transaction rather than trusted from
    browser-supplied identity data.
    """

    google_client = GoogleOAuthClient()

    google_client.ensure_configured()

    transaction_service = OAuthTransactionService()

    state, transaction = transaction_service.create(
        provider="google",
        mode="link",
        user_id=str(current_user.id),
    )

    authorization_url = (
        google_client.build_authorization_url(
            state=state,
            nonce=transaction.nonce,
            code_verifier=transaction.code_verifier,
        )
    )

    return OAuthStartResponse(
        authorization_url=authorization_url,
    )


@router.get(
    "/oauth/google/callback",
    response_class=RedirectResponse,
)
def google_oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db_session),
) -> RedirectResponse:
    oauth_service = OAuthAuthenticationService()

    result = oauth_service.authenticate_google_callback(
        db,
        code=code,
        state=state,
    )

    handoff_service = OAuthBrowserHandoffService()

    if result.transaction_mode == "link":
        if not result.transaction_user_id:
            raise RuntimeError(
                "OAuth link transaction has no bound user"
            )

        try:
            from uuid import UUID

            linking_user_id = UUID(
                result.transaction_user_id
            )
        except ValueError as exc:
            raise RuntimeError(
                "OAuth link transaction user is invalid"
            ) from exc

        user_repository = UserRepository()

        linking_user = user_repository.get_by_id(
            db,
            linking_user_id,
        )

        if linking_user is None:
            raise RuntimeError(
                "OAuth link user could not be found"
            )

        if not linking_user.is_active:
            raise RuntimeError(
                "OAuth link user is inactive"
            )

        identity_service = UserIdentityService(
            UserIdentityRepository(),
        )

        identity_service.link_identity(
            db,
            user_id=linking_user.id,
            provider=result.external_identity.provider,
            provider_subject=result.external_identity.subject,
            provider_email=result.external_identity.email,
            provider_email_verified=(
                result.external_identity.email_verified
            ),
        )

        db.commit()

        handoff_code = handoff_service.create(
            handoff=OAuthBrowserHandoff(
                status="linked",
                provider=result.external_identity.provider,
                email=result.external_identity.email,
                email_verified=(
                    result.external_identity.email_verified
                ),
                full_name=result.external_identity.full_name,
                picture_url=result.external_identity.picture_url,
            )
        )

    elif result.is_new_identity:
        pending_service = OAuthPendingIdentityService()

        continuation_token = pending_service.create(
            identity=result.external_identity,
        )

        handoff_code = handoff_service.create(
            handoff=OAuthBrowserHandoff(
                status="registration_required",
                continuation_token=continuation_token,
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
            )
        )

    else:
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

        handoff_code = handoff_service.create(
            handoff=OAuthBrowserHandoff(
                status="authenticated",
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
            )
        )

    redirect_url = (
        f"{settings.oauth_frontend_success_url}"
        f"?code={handoff_code}"
    )

    return RedirectResponse(
        url=redirect_url,
        status_code=303,
        headers={
            "Cache-Control": "no-store",
        },
    )


@router.post(
    "/oauth/handoff",
    response_model=OAuthHandoffResponse,
)
def consume_oauth_handoff(
    request: OAuthHandoffRequest,
) -> OAuthHandoffResponse:
    service = OAuthBrowserHandoffService()

    handoff = service.consume(
        code=request.code,
    )

    if handoff.status == "authenticated":
        if (
            not handoff.access_token
            or not handoff.refresh_token
        ):
            raise RuntimeError(
                "Authenticated OAuth handoff is incomplete"
            )

        return OAuthHandoffResponse(
            status="authenticated",
            tokens=TokenResponse(
                access_token=handoff.access_token,
                refresh_token=handoff.refresh_token,
            ),
        )

    if handoff.status == "linked":
        return OAuthHandoffResponse(
            status="linked",
            identity=OAuthIdentityPreview(
                provider=handoff.provider or "",
                email=handoff.email,
                email_verified=handoff.email_verified,
                full_name=handoff.full_name,
                picture_url=handoff.picture_url,
            ),
        )

    if handoff.status == "registration_required":
        if not handoff.continuation_token:
            raise RuntimeError(
                "Registration OAuth handoff is incomplete"
            )

        return OAuthHandoffResponse(
            status="registration_required",
            continuation_token=(
                handoff.continuation_token
            ),
            identity=OAuthIdentityPreview(
                provider=handoff.provider or "",
                email=handoff.email,
                email_verified=handoff.email_verified,
                full_name=handoff.full_name,
                picture_url=handoff.picture_url,
            ),
        )

    raise RuntimeError(
        "Unsupported OAuth handoff status"
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
