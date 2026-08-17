from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.clients.google_oauth_client import GoogleOAuthClient
from app.core.exceptions import PlatformException
from app.models.user import User
from app.models.user_identity import UserIdentity
from app.repositories.user_repository import UserRepository
from app.services.oauth_provider import ExternalIdentity
from app.services.oauth_transaction_service import (
    OAuthTransactionService,
)
from app.services.user_identity_service import UserIdentityService


@dataclass(frozen=True)
class OAuthAuthenticationResult:
    user: User | None
    identity: UserIdentity | None
    external_identity: ExternalIdentity
    is_new_identity: bool
    transaction_mode: str
    transaction_user_id: str | None


class OAuthAuthenticationService:
    """
    Orchestrate external authentication without using provider email
    as an account identity key.

    Provider + provider subject is authoritative.
    """

    def __init__(
        self,
        transaction_service: OAuthTransactionService | None = None,
        identity_service: UserIdentityService | None = None,
        user_repository: UserRepository | None = None,
        google_client: GoogleOAuthClient | None = None,
    ) -> None:
        self.transaction_service = (
            transaction_service
            or OAuthTransactionService()
        )

        self.identity_service = (
            identity_service
            or UserIdentityService()
        )

        self.user_repository = (
            user_repository
            or UserRepository()
        )

        self.google_client = (
            google_client
            or GoogleOAuthClient()
        )


    def authenticate_google_callback(
        self,
        db: Session,
        *,
        code: str,
        state: str,
    ) -> OAuthAuthenticationResult:
        """
        Validate a Google callback and resolve its Zevinq identity.

        Unknown provider identities are deliberately not linked or
        merged based on email.
        """

        transaction = self.transaction_service.consume(
            state=state,
            expected_provider="google",
        )

        tokens = self.google_client.exchange_code(
            code=code,
            code_verifier=transaction.code_verifier,
        )

        external_identity = (
            self.google_client.validate_identity(
                id_token=tokens.id_token,
                expected_nonce=transaction.nonce,
            )
        )

        identity = self.identity_service.resolve_identity(
            db,
            provider=external_identity.provider,
            provider_subject=external_identity.subject,
        )

        if identity is None:
            return OAuthAuthenticationResult(
                user=None,
                identity=None,
                external_identity=external_identity,
                is_new_identity=True,
                transaction_mode=transaction.mode,
                transaction_user_id=transaction.user_id,
            )

        user = self.user_repository.get_by_id(
            db,
            identity.user_id,
        )

        if user is None:
            raise PlatformException(
                message=(
                    "Linked Zevinq account could not be found"
                ),
                error_code="OAUTH_LINKED_USER_NOT_FOUND",
                status_code=401,
            )

        if not user.is_active:
            raise PlatformException(
                message="Zevinq account is inactive",
                error_code="OAUTH_USER_INACTIVE",
                status_code=403,
            )

        self.identity_service.record_login(
            db,
            identity=identity,
        )

        return OAuthAuthenticationResult(
            user=user,
            identity=identity,
            external_identity=external_identity,
            is_new_identity=False,
            transaction_mode=transaction.mode,
            transaction_user_id=transaction.user_id,
        )
