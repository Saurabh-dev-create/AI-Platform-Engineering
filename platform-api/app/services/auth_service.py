from sqlalchemy.orm import Session

from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
)
from app.auth.password import hash_password, verify_password
from app.core.exceptions import (
    AuthenticationFailedException,
    InactiveUserException,
    ResourceConflictException,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)


class AuthService:
    """
    Business logic for platform authentication and identity lifecycle.
    """

    def __init__(
        self,
        user_repository: UserRepository,
    ) -> None:
        self.user_repository = user_repository

    def register_user(
        self,
        db: Session,
        registration: RegisterRequest,
    ) -> User:
        normalized_email = registration.email.lower()

        existing_user = self.user_repository.get_by_email(
            db,
            normalized_email,
        )

        if existing_user is not None:
            raise ResourceConflictException(
                resource="User",
                field="email",
                value=normalized_email,
            )

        password_hash = hash_password(
            registration.password,
        )

        return self.user_repository.create(
            db,
            email=normalized_email,
            password_hash=password_hash,
            full_name=registration.full_name.strip(),
            )
    def login_user(
        self,
        db: Session,
        login: LoginRequest,
    ) -> TokenResponse:
        normalized_email = login.email.lower()

        user = self.user_repository.get_by_email(
            db,
            normalized_email,
        )

        if user is None:
            raise AuthenticationFailedException()

        if not verify_password(
            login.password,
            user.password_hash,
        ):
            raise AuthenticationFailedException()

        if not user.is_active:
            raise InactiveUserException()

        subject = str(user.id)

        access_token = create_access_token(
            subject=subject,
        )

        refresh_token = create_refresh_token(
            subject=subject,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
