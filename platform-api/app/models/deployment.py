from uuid import UUID

from sqlalchemy import (
    Enum,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import (
    DeploymentEnvironment,
    DeploymentStatus,
    DeploymentStrategy,
)
from app.database.base import Base, TimestampMixin, UUIDMixin


class Deployment(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Deployment request for an explicit AI agent version.

    A Deployment connects an immutable AgentVersion to a target
    environment and tracks its rollout strategy and lifecycle.

    Deployments intentionally reference AgentVersion rather than Agent
    so that releases remain reproducible, auditable, and suitable for
    future promotion, rollback, approval, GitOps, and Kubernetes
    execution workflows.
    """

    __tablename__ = "deployments"

    agent_version_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "agent_versions.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    environment: Mapped[DeploymentEnvironment] = mapped_column(
        Enum(
            DeploymentEnvironment,
            name="deployment_environment",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda enum_class: [
                member.value
                for member in enum_class
            ],
        ),
        nullable=False,
    )

    strategy: Mapped[DeploymentStrategy] = mapped_column(
        Enum(
            DeploymentStrategy,
            name="deployment_strategy",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda enum_class: [
                member.value
                for member in enum_class
            ],
        ),
        nullable=False,
        default=DeploymentStrategy.ROLLING,
    )

    status: Mapped[DeploymentStatus] = mapped_column(
        Enum(
            DeploymentStatus,
            name="deployment_status",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda enum_class: [
                member.value
                for member in enum_class
            ],
        ),
        nullable=False,
        default=DeploymentStatus.REQUESTED,
    )

    requested_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<Deployment "
            f"id={self.id} "
            f"agent_version_id={self.agent_version_id} "
            f"environment={self.environment} "
            f"strategy={self.strategy} "
            f"status={self.status}>"
        )
