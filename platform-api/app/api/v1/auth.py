from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies.database import get_db_session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.team_entitlement_repository import (
    TeamEntitlementRepository,
)
from app.repositories.team_membership_repository import (
    TeamMembershipRepository,
)
from app.repositories.team_repository import TeamRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.entitlement_service import EntitlementService
from app.services.self_service_onboarding_service import (
    SelfServiceOnboardingService,
)
from app.services.team_service import TeamService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
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
