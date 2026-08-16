from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import PlatformException
from app.models.user_identity import UserIdentity
from app.repositories.user_identity_repository import (
    UserIdentityRepository,
)


class UserIdentityService:
    """
    Business and security rules for external authentication identities.

    Provider subject identifiers, rather than email addresses, are the
    authoritative keys for external identities.
    """

    SUPPORTED_PROVIDERS = {
        "google",
        "github",
        "linkedin",
    }

    def __init__(
        self,
        repository: UserIdentityRepository | None = None,
    ) -> None:
        self.repository = (
            repository
            or UserIdentityRepository()
        )


    def _normalize_provider(
        self,
        provider: str,
    ) -> str:
        normalized = provider.strip().lower()

        if normalized not in self.SUPPORTED_PROVIDERS:
            raise PlatformException(
                message="Unsupported identity provider",
                error_code="IDENTITY_PROVIDER_UNSUPPORTED",
                status_code=400,
                details={
                    "provider": normalized,
                },
            )

        return normalized


    def resolve_identity(
        self,
        db: Session,
        *,
        provider: str,
        provider_subject: str,
    ) -> UserIdentity | None:
        """
        Resolve an existing provider identity.

        Email is intentionally not used for identity resolution.
        """

        normalized_provider = self._normalize_provider(
            provider
        )

        normalized_subject = provider_subject.strip()

        if not normalized_subject:
            raise PlatformException(
                message="Identity provider subject is required",
                error_code="IDENTITY_SUBJECT_REQUIRED",
                status_code=400,
            )

        return self.repository.get_by_provider_subject(
            db,
            provider=normalized_provider,
            provider_subject=normalized_subject,
        )


    def link_identity(
        self,
        db: Session,
        *,
        user_id: UUID,
        provider: str,
        provider_subject: str,
        provider_email: str | None,
        provider_email_verified: bool,
    ) -> UserIdentity:
        """
        Explicitly link a provider identity to a Zevinq user.

        This method never links accounts merely because provider email
        matches a Zevinq account email.
        """

        normalized_provider = self._normalize_provider(
            provider
        )

        normalized_subject = provider_subject.strip()

        if not normalized_subject:
            raise PlatformException(
                message="Identity provider subject is required",
                error_code="IDENTITY_SUBJECT_REQUIRED",
                status_code=400,
            )

        existing = (
            self.repository.get_by_provider_subject(
                db,
                provider=normalized_provider,
                provider_subject=normalized_subject,
            )
        )

        if existing is not None:
            if existing.user_id == user_id:
                return existing

            raise PlatformException(
                message=(
                    "External identity is already linked "
                    "to another account"
                ),
                error_code="IDENTITY_ALREADY_LINKED",
                status_code=409,
            )

        normalized_email = None

        if provider_email:
            normalized_email = (
                provider_email.strip().lower()
            )

        return self.repository.create(
            db,
            user_id=user_id,
            provider=normalized_provider,
            provider_subject=normalized_subject,
            provider_email=normalized_email,
            provider_email_verified=(
                provider_email_verified
            ),
            last_login_at=None,
        )


    def record_login(
        self,
        db: Session,
        *,
        identity: UserIdentity,
    ) -> UserIdentity:
        """
        Record successful use of an external identity.
        """

        return self.repository.update_last_login(
            db,
            identity=identity,
            last_login_at=datetime.now(UTC),
        )


    def list_identities(
        self,
        db: Session,
        *,
        user_id: UUID,
    ) -> list[UserIdentity]:
        """
        Return authentication identities linked to a user.
        """

        return self.repository.list_for_user(
            db,
            user_id=user_id,
        )
