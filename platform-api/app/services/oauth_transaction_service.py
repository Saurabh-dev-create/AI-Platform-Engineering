import json
import secrets
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Literal

from redis import Redis

from app.clients.redis_client import get_redis_client
from app.config.settings import settings
from app.core.exceptions import PlatformException


OAuthMode = Literal[
    "login",
    "link",
]


@dataclass(frozen=True)
class OAuthTransaction:
    provider: str
    nonce: str
    code_verifier: str
    mode: OAuthMode
    created_at: str


class OAuthTransactionService:
    """
    Manage short-lived, single-use OAuth authorization transactions.

    OAuth state is stored in Redis so it can be shared safely across
    multiple Platform API replicas.
    """

    KEY_PREFIX = "oauth:transaction:"

    def __init__(
        self,
        redis_client: Redis | None = None,
    ) -> None:
        self.redis = (
            redis_client
            or get_redis_client()
        )


    def create(
        self,
        *,
        provider: str,
        mode: OAuthMode = "login",
    ) -> tuple[str, OAuthTransaction]:
        """
        Create a new OAuth state and nonce pair.
        """

        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(64)

        transaction = OAuthTransaction(
            provider=provider.strip().lower(),
            nonce=nonce,
            code_verifier=code_verifier,
            mode=mode,
            created_at=datetime.now(UTC).isoformat(),
        )

        key = self._key(state)

        created = self.redis.set(
            key,
            json.dumps(asdict(transaction)),
            ex=settings.oauth_state_ttl_seconds,
            nx=True,
        )

        if not created:
            raise PlatformException(
                message="Unable to create OAuth transaction",
                error_code="OAUTH_TRANSACTION_CREATE_FAILED",
                status_code=500,
            )

        return state, transaction


    def consume(
        self,
        *,
        state: str,
        expected_provider: str,
    ) -> OAuthTransaction:
        """
        Atomically consume a single-use OAuth transaction.

        Redis GETDEL ensures a successfully consumed state cannot be
        replayed by another callback.
        """

        normalized_state = state.strip()

        if not normalized_state:
            raise PlatformException(
                message="OAuth state is required",
                error_code="OAUTH_STATE_REQUIRED",
                status_code=400,
            )

        raw_transaction = self.redis.getdel(
            self._key(normalized_state)
        )

        if raw_transaction is None:
            raise PlatformException(
                message=(
                    "OAuth transaction is invalid, expired, "
                    "or already used"
                ),
                error_code="OAUTH_STATE_INVALID",
                status_code=400,
            )

        try:
            data = json.loads(raw_transaction)

            transaction = OAuthTransaction(
                provider=data["provider"],
                nonce=data["nonce"],
                code_verifier=data["code_verifier"],
                mode=data["mode"],
                created_at=data["created_at"],
            )
        except (
            KeyError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            raise PlatformException(
                message="OAuth transaction data is invalid",
                error_code="OAUTH_TRANSACTION_INVALID",
                status_code=400,
            ) from exc

        normalized_provider = (
            expected_provider.strip().lower()
        )

        if transaction.provider != normalized_provider:
            raise PlatformException(
                message="OAuth provider does not match transaction",
                error_code="OAUTH_PROVIDER_MISMATCH",
                status_code=400,
            )

        return transaction


    def _key(
        self,
        state: str,
    ) -> str:
        return (
            f"{self.KEY_PREFIX}"
            f"{state}"
        )
