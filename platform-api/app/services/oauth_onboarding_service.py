from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.exceptions import PlatformException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.team import TeamCreate
from app.services.entitlement_service import EntitlementService
from app.services.oauth_pending_identity_service import (
    OAuthPendingIdentityService,
)
from app.services.team_service import TeamService
from app.services.user_identity_service import UserIdentityService


@dataclass(frozen=True)
class OAuthOnboardingResult:
    user: User


class OAuthOnboardingService:
    """
    Provision a new Zevinq account from a verified external identity.

    User, workspace, membership, Free entitlement, and external
    identity are created in one database transaction.
    """

    def __init__(
        self,
        *,
        user_repository: UserRepository,
        pending_identity_service: OAuthPendingIdentityService,
        identity_service: UserIdentityService,
        team_service: TeamService,
        entitlement_service: EntitlementService,
    ) -> None:
        self.user_repository = user_repository
        self.pending_identity_service = pending_identity_service
        self.identity_service = identity_service
        self.team_service = team_service
        self.entitlement_service = entitlement_service

    def register_free_user(
        self,
        db: Session,
        *,
        continuation_token: str,
    ) -> OAuthOnboardingResult:
        pending = self.pending_identity_service.get(
            continuation_token=continuation_token,
        )

        if not pending.email:
            raise PlatformException(
                message=(
                    "A verified email address is required "
                    "to create a Zevinq account"
                ),
                error_code="OAUTH_EMAIL_REQUIRED",
                status_code=400,
            )

        if not pending.email_verified:
            raise PlatformException(
                message=(
                    "The external provider email address "
                    "must be verified"
                ),
                error_code="OAUTH_EMAIL_NOT_VERIFIED",
                status_code=400,
            )

        normalized_email = pending.email.strip().lower()

        existing_user = self.user_repository.get_by_email(
            db,
            normalized_email,
        )

        if existing_user is not None:
            raise PlatformException(
                message=(
                    "A Zevinq account already uses this email. "
                    "Sign in to that account and link this "
                    "identity from account settings."
                ),
                error_code="OAUTH_EMAIL_ACCOUNT_EXISTS",
                status_code=409,
            )

        existing_identity = self.identity_service.resolve_identity(
            db,
            provider=pending.provider,
            provider_subject=pending.subject,
        )

        if existing_identity is not None:
            raise PlatformException(
                message=(
                    "This external identity is already linked "
                    "to a Zevinq account"
                ),
                error_code="OAUTH_IDENTITY_ALREADY_LINKED",
                status_code=409,
            )

        full_name = (
            pending.full_name.strip()
            if pending.full_name
            and pending.full_name.strip()
            else normalized_email.split("@", 1)[0]
        )

        try:
            user = self.user_repository.create(
                db,
                email=normalized_email,
                password_hash=None,
                full_name=full_name,
            )

            workspace = self.team_service.provision_team(
                db,
                current_user=user,
                team_data=TeamCreate(
                    name=f"{user.full_name}'s Workspace",
                    slug=f"workspace-{user.id}",
                    description=(
                        "Personal Zevinq Free workspace."
                    ),
                ),
            )

            self.entitlement_service.create_free_entitlement(
                db,
                team_id=workspace.id,
            )

            self.identity_service.link_identity(
                db,
                user_id=user.id,
                provider=pending.provider,
                provider_subject=pending.subject,
                provider_email=pending.email,
                provider_email_verified=(
                    pending.email_verified
                ),
            )

            db.commit()

            self.pending_identity_service.delete(
                continuation_token=continuation_token,
            )

            return OAuthOnboardingResult(
                user=user,
            )

        except Exception:
            db.rollback()
            raise
