from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDMixin


class Project(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Team-owned AI platform project.

    Projects group AI agents, deployments, usage, budgets,
    policies, and operational ownership within a team.
    """

    __tablename__ = "projects"

    __table_args__ = (
        UniqueConstraint(
            "team_id",
            "slug",
            name="uq_projects_team_id_slug",
        ),
    )

    team_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "teams.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
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
            f"<Project "
            f"id={self.id} "
            f"team_id={self.team_id} "
            f"slug={self.slug!r} "
            f"is_active={self.is_active}>"
        )
