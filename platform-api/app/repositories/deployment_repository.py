from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import (
    DeploymentEnvironment,
    DeploymentStatus,
    DeploymentStrategy,
)
from app.models.agent import Agent
from app.models.agent_version import AgentVersion
from app.models.deployment import Deployment
from app.models.project import Project
from app.models.team_membership import TeamMembership


class DeploymentRepository:
    """
    Database access layer for AI agent deployments.

    Deployment ownership is resolved through the immutable AgentVersion
    and its parent Agent, Project, and Team membership hierarchy.
    """

    def get_for_user_by_id(
        self,
        db: Session,
        *,
        deployment_id: UUID,
        user_id: UUID,
    ) -> Deployment | None:
        """
        Return a deployment only when the requesting user belongs to
        the team that owns the deployed agent version.
        """

        statement = (
            select(Deployment)
            .join(
                AgentVersion,
                AgentVersion.id == Deployment.agent_version_id,
            )
            .join(
                Agent,
                Agent.id == AgentVersion.agent_id,
            )
            .join(
                Project,
                Project.id == Agent.project_id,
            )
            .join(
                TeamMembership,
                TeamMembership.team_id == Project.team_id,
            )
            .where(
                Deployment.id == deployment_id,
                TeamMembership.user_id == user_id,
            )
        )

        return db.scalar(statement)

    def list_for_agent_version(
        self,
        db: Session,
        *,
        agent_version_id: UUID,
    ) -> list[Deployment]:
        """
        Return deployments created for a specific immutable agent version.
        """

        statement = (
            select(Deployment)
            .where(
                Deployment.agent_version_id == agent_version_id,
            )
            .order_by(Deployment.created_at)
        )

        return list(
            db.scalars(statement).all()
        )

    def create(
        self,
        db: Session,
        *,
        agent_version_id: UUID,
        environment: DeploymentEnvironment,
        strategy: DeploymentStrategy,
        requested_by_user_id: UUID,
    ) -> Deployment:
        deployment = Deployment(
            agent_version_id=agent_version_id,
            environment=environment,
            strategy=strategy,
            status=DeploymentStatus.REQUESTED,
            requested_by_user_id=requested_by_user_id,
        )

        db.add(deployment)
        db.flush()
        db.refresh(deployment)

        return deployment

    def update_status(
        self,
        db: Session,
        *,
        deployment: Deployment,
        status: DeploymentStatus,
        failure_reason: str | None = None,
    ) -> Deployment:
        """
        Persist a Deployment lifecycle status change.

        Lifecycle transition validation belongs to the service layer.
        """

        deployment.status = status
        deployment.failure_reason = failure_reason

        db.flush()
        db.refresh(deployment)

        return deployment
