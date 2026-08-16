from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import (
    Base,
    TimestampMixin,
    UUIDMixin,
)


class UserIdentity(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    External authentication identity linked to a Zevinq user.

    Provider identities are deliberately separated from the platform
    user so one Zevinq account can authenticate through multiple
    identity providers without using email as the identity key.
    """

    __tablename__ = "user_identities"

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_subject",
            name=(
                "uq_user_identities_"
                "provider_subject"
            ),
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    provider_subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    provider_email: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
    )

    provider_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<UserIdentity "
            f"id={self.id} "
            f"user_id={self.user_id} "
            f"provider={self.provider!r}>"
        )
