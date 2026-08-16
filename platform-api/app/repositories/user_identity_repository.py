from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_identity import UserIdentity


class UserIdentityRepository:
    """
    Database access layer for external authentication identities.
    """

    def get_by_provider_subject(
        self,
        db: Session,
        *,
        provider: str,
        provider_subject: str,
    ) -> UserIdentity | None:
        statement = (
            select(UserIdentity)
            .where(
                UserIdentity.provider == provider,
                UserIdentity.provider_subject
                == provider_subject,
            )
        )

        return db.scalar(statement)


    def list_for_user(
        self,
        db: Session,
        *,
        user_id: UUID,
    ) -> list[UserIdentity]:
        statement = (
            select(UserIdentity)
            .where(
                UserIdentity.user_id == user_id,
            )
            .order_by(
                UserIdentity.created_at,
            )
        )

        return list(
            db.scalars(statement).all()
        )


    def create(
        self,
        db: Session,
        *,
        user_id: UUID,
        provider: str,
        provider_subject: str,
        provider_email: str | None,
        provider_email_verified: bool,
        last_login_at: datetime | None = None,
    ) -> UserIdentity:
        identity = UserIdentity(
            user_id=user_id,
            provider=provider,
            provider_subject=provider_subject,
            provider_email=provider_email,
            provider_email_verified=(
                provider_email_verified
            ),
            last_login_at=last_login_at,
        )

        db.add(identity)
        db.flush()
        db.refresh(identity)

        return identity


    def update_last_login(
        self,
        db: Session,
        *,
        identity: UserIdentity,
        last_login_at: datetime,
    ) -> UserIdentity:
        identity.last_login_at = last_login_at

        db.flush()
        db.refresh(identity)

        return identity
