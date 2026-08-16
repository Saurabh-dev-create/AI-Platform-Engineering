import base64
from dataclasses import dataclass
import hashlib
import secrets
from urllib.parse import urlencode

import httpx
import jwt
from jwt import PyJWKClient

from app.config.settings import settings
from app.core.exceptions import PlatformException
from app.services.oauth_provider import ExternalIdentity


@dataclass(frozen=True)
class GoogleTokenResponse:
    id_token: str
    access_token: str | None


class GoogleOAuthClient:
    """
    Google OpenID Connect provider adapter.

    Google-specific responses are normalized before leaving this client.
    """

    AUTHORIZATION_ENDPOINT = (
        "https://accounts.google.com/o/oauth2/v2/auth"
    )

    TOKEN_ENDPOINT = (
        "https://oauth2.googleapis.com/token"
    )

    JWKS_URI = (
        "https://www.googleapis.com/oauth2/v3/certs"
    )

    ISSUERS = {
        "https://accounts.google.com",
        "accounts.google.com",
    }

    SCOPES = (
        "openid",
        "email",
        "profile",
    )


    def is_configured(self) -> bool:
        return bool(
            settings.google_oauth_client_id
            and settings.google_oauth_client_secret
            and settings.google_oauth_redirect_uri
        )


    def ensure_configured(self) -> None:
        if not self.is_configured():
            raise PlatformException(
                message="Google authentication is not configured",
                error_code="GOOGLE_OAUTH_NOT_CONFIGURED",
                status_code=503,
            )


    def build_authorization_url(
        self,
        *,
        state: str,
        nonce: str,
        code_verifier: str,
    ) -> str:
        self.ensure_configured()

        code_challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(
                    code_verifier.encode("ascii")
                ).digest()
            )
            .decode("ascii")
            .rstrip("=")
        )

        params = {
            "client_id": settings.google_oauth_client_id,
            "redirect_uri": settings.google_oauth_redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.SCOPES),
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        return (
            f"{self.AUTHORIZATION_ENDPOINT}?"
            f"{urlencode(params)}"
        )


    def exchange_code(
        self,
        *,
        code: str,
        code_verifier: str,
    ) -> GoogleTokenResponse:
        self.ensure_configured()

        normalized_code = code.strip()

        if not normalized_code:
            raise PlatformException(
                message="Google authorization code is required",
                error_code="GOOGLE_AUTHORIZATION_CODE_REQUIRED",
                status_code=400,
            )

        try:
            response = httpx.post(
                self.TOKEN_ENDPOINT,
                data={
                    "code": normalized_code,
                    "client_id": (
                        settings.google_oauth_client_id
                    ),
                    "client_secret": (
                        settings.google_oauth_client_secret
                    ),
                    "redirect_uri": (
                        settings.google_oauth_redirect_uri
                    ),
                    "grant_type": "authorization_code",
                    "code_verifier": code_verifier,
                },
                timeout=10.0,
            )
        except httpx.HTTPError as exc:
            raise PlatformException(
                message="Unable to contact Google authentication service",
                error_code="GOOGLE_OAUTH_UPSTREAM_ERROR",
                status_code=502,
            ) from exc

        if response.status_code != 200:
            raise PlatformException(
                message="Google authorization code exchange failed",
                error_code="GOOGLE_TOKEN_EXCHANGE_FAILED",
                status_code=401,
            )

        data = response.json()

        id_token = data.get("id_token")

        if not isinstance(id_token, str) or not id_token:
            raise PlatformException(
                message="Google did not return an ID token",
                error_code="GOOGLE_ID_TOKEN_MISSING",
                status_code=401,
            )

        access_token = data.get("access_token")

        if not isinstance(access_token, str):
            access_token = None

        return GoogleTokenResponse(
            id_token=id_token,
            access_token=access_token,
        )


    def validate_identity(
        self,
        *,
        id_token: str,
        expected_nonce: str,
    ) -> ExternalIdentity:
        self.ensure_configured()

        try:
            jwks_client = PyJWKClient(
                self.JWKS_URI,
                cache_keys=True,
            )

            signing_key = (
                jwks_client.get_signing_key_from_jwt(
                    id_token
                )
            )

            claims = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.google_oauth_client_id,
                issuer=list(self.ISSUERS),
                options={
                    "require": [
                        "exp",
                        "iat",
                        "iss",
                        "aud",
                        "sub",
                    ],
                },
            )
        except jwt.PyJWTError as exc:
            raise PlatformException(
                message="Google identity token is invalid",
                error_code="GOOGLE_ID_TOKEN_INVALID",
                status_code=401,
            ) from exc

        token_nonce = claims.get("nonce")

        if (
            not isinstance(token_nonce, str)
            or not expected_nonce
            or not secrets.compare_digest(
                token_nonce,
                expected_nonce,
            )
        ):
            raise PlatformException(
                message="Google identity nonce is invalid",
                error_code="GOOGLE_NONCE_INVALID",
                status_code=401,
            )

        subject = claims.get("sub")

        if not isinstance(subject, str) or not subject:
            raise PlatformException(
                message="Google identity subject is missing",
                error_code="GOOGLE_SUBJECT_MISSING",
                status_code=401,
            )

        email = claims.get("email")

        if not isinstance(email, str):
            email = None

        full_name = claims.get("name")

        if not isinstance(full_name, str):
            full_name = None

        picture_url = claims.get("picture")

        if not isinstance(picture_url, str):
            picture_url = None

        return ExternalIdentity(
            provider="google",
            subject=subject,
            email=email.lower() if email else None,
            email_verified=bool(
                claims.get("email_verified", False)
            ),
            full_name=full_name,
            picture_url=picture_url,
        )
