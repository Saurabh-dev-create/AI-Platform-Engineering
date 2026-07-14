from pwdlib import PasswordHash

from app.config.settings import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using the configured password hasher.

    Plaintext passwords must never be stored in the platform database.
    """

    if len(password) < settings.password_min_length:
        raise ValueError(
            f"Password must be at least "
            f"{settings.password_min_length} characters long"
        )

    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plaintext password against a stored password hash.
    """

    return password_hash.verify(
        plain_password,
        hashed_password,
    )
