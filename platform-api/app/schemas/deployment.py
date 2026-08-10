from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.constants import (
    DeploymentEnvironment,
    DeploymentStatus,
    DeploymentStrategy,
)


class DeploymentCreate(BaseModel):
    """
    Request schema for creating a deployment of an explicit agent version.

    Deployment lifecycle status and requester identity are controlled
    by the platform. Clients select the immutable AgentVersion,
    target environment, and rollout strategy.
    """

    agent_version_id: UUID
    environment: DeploymentEnvironment
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING


class DeploymentResponse(BaseModel):
    """
    Response schema for an AI agent deployment.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    agent_version_id: UUID

    environment: DeploymentEnvironment
    strategy: DeploymentStrategy
    status: DeploymentStatus

    requested_by_user_id: UUID | None
    failure_reason: str | None

    created_at: datetime
    updated_at: datetime


class DeploymentTransition(BaseModel):
    """
    Request schema for transitioning a deployment lifecycle state.

    The service layer remains responsible for validating whether the
    requested transition is legal for the deployment's current state.
    """

    status: DeploymentStatus
    failure_reason: str | None = None
