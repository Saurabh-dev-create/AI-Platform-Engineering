from uuid import UUID

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import AgentVersionStatus
from app.database.base import Base, TimestampMixin, UUIDMixin


class AgentVersion(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Immutable versioned configuration for a registered AI agent.

    AgentVersion captures the model, prompt, runtime, and tool
    configuration used by a specific version of an agent.

    Deployments will reference explicit agent versions so that
    releases can be reproduced, rolled back, audited, and promoted
    safely between environments.
    """

    __tablename__ = "agent_versions"

    __table_args__ = (
        UniqueConstraint(
            "agent_id",
            "version_number",
            name="uq_agent_versions_agent_id_version_number",
        ),
    )

    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "agents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[AgentVersionStatus] = mapped_column(
        Enum(
            AgentVersionStatus,
            name="agent_version_status",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda enum_class: [
                member.value
                for member in enum_class
            ],
        ),
        nullable=False,
        default=AgentVersionStatus.DRAFT,
    )

    model_config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    prompt_template: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    runtime_config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    tool_config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    change_summary: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    created_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<AgentVersion "
            f"id={self.id} "
            f"agent_id={self.agent_id} "
            f"version_number={self.version_number} "
            f"status={self.status}>"
        )
