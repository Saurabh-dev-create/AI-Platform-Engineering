from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import AgentStatus
from app.database.base import Base, TimestampMixin, UUIDMixin


class Agent(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Logical AI agent registered under a team-owned project.

    Agent identity is kept separate from versioned model, prompt,
    runtime, and deployment configuration.
    """

    __tablename__ = "agents"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "slug",
            name="uq_agents_project_id_slug",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "projects.id",
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

    status: Mapped[AgentStatus] = mapped_column(
        Enum(
            AgentStatus,
            name="agent_status",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda enum_class: [
                member.value
                for member in enum_class
            ],
        ),
        nullable=False,
        default=AgentStatus.DRAFT,
    )

    def __repr__(self) -> str:
        return (
            f"<Agent "
            f"id={self.id} "
            f"project_id={self.project_id} "
            f"slug={self.slug!r} "
            f"status={self.status}>"
        )
