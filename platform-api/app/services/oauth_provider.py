from dataclasses import dataclass


@dataclass(frozen=True)
class ExternalIdentity:
    """
    Normalized identity returned by an external authentication provider.
    """

    provider: str
    subject: str
    email: str | None
    email_verified: bool
    full_name: str | None
    picture_url: str | None
