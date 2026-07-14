from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDMixin


class Team(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Tenant boundary for the AI Agent Platform.

    Teams own projects, AI agents, deployments, budgets, quotas,
    and governance policies.
    """

    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Team "
            f"id={self.id} "
            f"slug={self.slug!r} "
            f"is_active={self.is_active}>"
        )
