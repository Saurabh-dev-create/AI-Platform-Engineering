import json
import secrets
from dataclasses import asdict, dataclass

from redis import Redis

from app.clients.redis_client import get_redis_client
from app.core.exceptions import PlatformException
from app.services.oauth_provider import ExternalIdentity


@dataclass(frozen=True)
class PendingOAuthIdentity:
    provider: str
    subject: str
    email: str | None
    email_verified: bool
    full_name: str | None
    picture_url: str | None


class OAuthPendingIdentityService:
    """
    Store verified external identities while the user chooses
    registration or account-linking.

    The browser receives only an opaque continuation token.
    """

    KEY_PREFIX = "oauth:pending:"
    TTL_SECONDS = 600

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
        identity: ExternalIdentity,
    ) -> str:
        continuation_token = secrets.token_urlsafe(32)

        pending = PendingOAuthIdentity(
            provider=identity.provider,
            subject=identity.subject,
            email=identity.email,
            email_verified=identity.email_verified,
            full_name=identity.full_name,
            picture_url=identity.picture_url,
        )

        created = self.redis.set(
            self._key(continuation_token),
            json.dumps(asdict(pending)),
            ex=self.TTL_SECONDS,
            nx=True,
        )

        if not created:
            raise PlatformException(
                message=(
                    "Unable to create OAuth continuation"
                ),
                error_code="OAUTH_CONTINUATION_CREATE_FAILED",
                status_code=500,
            )

        return continuation_token


    def get(
        self,
        *,
        continuation_token: str,
    ) -> PendingOAuthIdentity:
        """
        Read a pending verified identity without consuming it.

        Used while deciding between new-account registration and
        explicit linking to an existing Zevinq account.
        """

        normalized_token = continuation_token.strip()

        if not normalized_token:
            raise PlatformException(
                message="OAuth continuation token is required",
                error_code="OAUTH_CONTINUATION_REQUIRED",
                status_code=400,
            )

        raw = self.redis.get(
            self._key(normalized_token)
        )

        if raw is None:
            raise PlatformException(
                message=(
                    "OAuth continuation is invalid, expired, "
                    "or already used"
                ),
                error_code="OAUTH_CONTINUATION_INVALID",
                status_code=400,
            )

        return self._deserialize(raw)


    def delete(
        self,
        *,
        continuation_token: str,
    ) -> None:
        """
        Delete a completed OAuth continuation.
        """

        self.redis.delete(
            self._key(
                continuation_token.strip()
            )
        )


    def consume(
        self,
        *,
        continuation_token: str,
    ) -> PendingOAuthIdentity:
        normalized_token = continuation_token.strip()

        if not normalized_token:
            raise PlatformException(
                message="OAuth continuation token is required",
                error_code="OAUTH_CONTINUATION_REQUIRED",
                status_code=400,
            )

        raw = self.redis.getdel(
            self._key(normalized_token)
        )

        if raw is None:
            raise PlatformException(
                message=(
                    "OAuth continuation is invalid, expired, "
                    "or already used"
                ),
                error_code="OAUTH_CONTINUATION_INVALID",
                status_code=400,
            )

        return self._deserialize(raw)


    def _deserialize(
        self,
        raw: str,
    ) -> PendingOAuthIdentity:
        try:
            data = json.loads(raw)

            return PendingOAuthIdentity(
                provider=data["provider"],
                subject=data["subject"],
                email=data.get("email"),
                email_verified=bool(
                    data["email_verified"]
                ),
                full_name=data.get("full_name"),
                picture_url=data.get("picture_url"),
            )

        except (
            KeyError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            raise PlatformException(
                message="OAuth continuation data is invalid",
                error_code="OAUTH_CONTINUATION_DATA_INVALID",
                status_code=400,
            ) from exc


    def _key(
        self,
        token: str,
    ) -> str:
        return f"{self.KEY_PREFIX}{token}"
