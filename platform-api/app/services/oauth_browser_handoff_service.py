import json
import secrets
from dataclasses import asdict, dataclass
from typing import Literal

from redis import Redis

from app.clients.redis_client import get_redis_client
from app.core.exceptions import PlatformException


OAuthHandoffStatus = Literal[
    "authenticated",
    "registration_required",
    "linked",
]


@dataclass(frozen=True)
class OAuthBrowserHandoff:
    status: OAuthHandoffStatus

    access_token: str | None = None
    refresh_token: str | None = None

    continuation_token: str | None = None

    provider: str | None = None
    email: str | None = None
    email_verified: bool = False
    full_name: str | None = None
    picture_url: str | None = None


class OAuthBrowserHandoffService:
    """
    Transfer OAuth results from the server-side provider callback
    to the frontend without exposing Zevinq tokens in redirect URLs.
    """

    KEY_PREFIX = "oauth:handoff:"
    TTL_SECONDS = 120

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
        handoff: OAuthBrowserHandoff,
    ) -> str:
        code = secrets.token_urlsafe(32)

        created = self.redis.set(
            self._key(code),
            json.dumps(
                asdict(handoff)
            ),
            ex=self.TTL_SECONDS,
            nx=True,
        )

        if not created:
            raise PlatformException(
                message=(
                    "Unable to create OAuth browser handoff"
                ),
                error_code="OAUTH_HANDOFF_CREATE_FAILED",
                status_code=500,
            )

        return code

    def consume(
        self,
        *,
        code: str,
    ) -> OAuthBrowserHandoff:
        normalized_code = code.strip()

        if not normalized_code:
            raise PlatformException(
                message="OAuth handoff code is required",
                error_code="OAUTH_HANDOFF_REQUIRED",
                status_code=400,
            )

        raw = self.redis.getdel(
            self._key(normalized_code)
        )

        if raw is None:
            raise PlatformException(
                message=(
                    "OAuth handoff is invalid, expired, "
                    "or already used"
                ),
                error_code="OAUTH_HANDOFF_INVALID",
                status_code=400,
            )

        try:
            data = json.loads(raw)

            return OAuthBrowserHandoff(
                status=data["status"],
                access_token=data.get(
                    "access_token"
                ),
                refresh_token=data.get(
                    "refresh_token"
                ),
                continuation_token=data.get(
                    "continuation_token"
                ),
                provider=data.get("provider"),
                email=data.get("email"),
                email_verified=bool(
                    data.get(
                        "email_verified",
                        False,
                    )
                ),
                full_name=data.get(
                    "full_name"
                ),
                picture_url=data.get(
                    "picture_url"
                ),
            )

        except (
            KeyError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            raise PlatformException(
                message="OAuth handoff data is invalid",
                error_code="OAUTH_HANDOFF_DATA_INVALID",
                status_code=400,
            ) from exc

    def _key(
        self,
        code: str,
    ) -> str:
        return (
            f"{self.KEY_PREFIX}"
            f"{code}"
        )
