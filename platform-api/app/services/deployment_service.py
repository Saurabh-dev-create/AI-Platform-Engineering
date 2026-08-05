from uuid import UUID

from sqlalchemy.orm import Session

from app.core.constants import (
    AgentVersionStatus,
    DeploymentStatus,
    TeamRole,
)
from app.core.exceptions import (
    PlatformException,
    ResourceNotFoundException,
)
from app.models.deployment import Deployment
from app.models.user import User
from app.repositories.agent_repository import AgentRepository
from app.repositories.agent_version_repository import AgentVersionRepository
from app.repositories.deployment_repository import DeploymentRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.team_membership_repository import (
    TeamMembershipRepository,
)
from app.schemas.deployment import DeploymentCreate


class DeploymentService:
    """
    Business logic for tenant-scoped AI agent deployment lifecycle.
    """

    ALLOWED_TRANSITIONS: dict[
        DeploymentStatus,
        set[DeploymentStatus],
    ] = {
        DeploymentStatus.REQUESTED: {
            DeploymentStatus.PENDING_APPROVAL,
            DeploymentStatus.APPROVED,
        },
        DeploymentStatus.PENDING_APPROVAL: {
            DeploymentStatus.APPROVED,
        },
        DeploymentStatus.APPROVED: {
            DeploymentStatus.DEPLOYING,
        },
        DeploymentStatus.DEPLOYING: {
            DeploymentStatus.RUNNING,
            DeploymentStatus.FAILED,
        },
        DeploymentStatus.RUNNING: {
            DeploymentStatus.TERMINATED,
        },
        DeploymentStatus.FAILED: {
            DeploymentStatus.TERMINATED,
        },
        DeploymentStatus.TERMINATED: set(),
    }

    def __init__(
        self,
        deployment_repository: DeploymentRepository,
        version_repository: AgentVersionRepository,
        agent_repository: AgentRepository,
        project_repository: ProjectRepository,
        membership_repository: TeamMembershipRepository,
    ) -> None:
        self.deployment_repository = deployment_repository
        self.version_repository = version_repository
        self.agent_repository = agent_repository
        self.project_repository = project_repository
        self.membership_repository = membership_repository

    def _require_version_access(
        self,
        db: Session,
        *,
        version_id: UUID,
        current_user: User,
    ) -> tuple:
        version = self.version_repository.get_for_user_by_id(
            db,
            version_id=version_id,
            user_id=current_user.id,
        )

        if version is None:
            raise ResourceNotFoundException(
                resource="AgentVersion",
                resource_id=str(version_id),
            )

        agent = self.agent_repository.get_for_user_by_id(
            db,
            agent_id=version.agent_id,
            user_id=current_user.id,
        )

        if agent is None:
            raise ResourceNotFoundException(
                resource="AgentVersion",
                resource_id=str(version_id),
            )

        project = self.project_repository.get_for_user_by_id(
            db,
            project_id=agent.project_id,
            user_id=current_user.id,
        )

        if project is None:
            raise ResourceNotFoundException(
                resource="AgentVersion",
                resource_id=str(version_id),
            )

        membership = self.membership_repository.get_by_user_and_team(
            db,
            user_id=current_user.id,
            team_id=project.team_id,
        )

        if membership is None:
            raise ResourceNotFoundException(
                resource="AgentVersion",
                resource_id=str(version_id),
            )

        return version, membership.role

    def create_deployment(
        self,
        db: Session,
        *,
        current_user: User,
        deployment_data: DeploymentCreate,
    ) -> Deployment:
        version, role = self._require_version_access(
            db,
            version_id=deployment_data.agent_version_id,
            current_user=current_user,
        )

        if role not in {
            TeamRole.TEAM_ADMIN,
            TeamRole.DEVELOPER,
        }:
            raise PlatformException(
                message=(
                    "Deployment creation requires "
                    "team_admin or developer role"
                ),
                error_code="DEPLOYMENT_CREATE_FORBIDDEN",
                status_code=403,
            )

        if version.status != AgentVersionStatus.PUBLISHED:
            raise PlatformException(
                message=(
                    "Only published agent versions can be deployed"
                ),
                error_code="AGENT_VERSION_NOT_DEPLOYABLE",
                status_code=409,
            )

        deployment = self.deployment_repository.create(
            db,
            agent_version_id=version.id,
            environment=deployment_data.environment,
            strategy=deployment_data.strategy,
            requested_by_user_id=current_user.id,
        )

        db.commit()
        db.refresh(deployment)

        return deployment

    def get_deployment(
        self,
        db: Session,
        *,
        deployment_id: UUID,
        current_user: User,
    ) -> Deployment:
        deployment = self.deployment_repository.get_for_user_by_id(
            db,
            deployment_id=deployment_id,
            user_id=current_user.id,
        )

        if deployment is None:
            raise ResourceNotFoundException(
                resource="Deployment",
                resource_id=str(deployment_id),
            )

        return deployment

    def list_deployments_for_version(
        self,
        db: Session,
        *,
        version_id: UUID,
        current_user: User,
    ) -> list[Deployment]:
        self._require_version_access(
            db,
            version_id=version_id,
            current_user=current_user,
        )

        return self.deployment_repository.list_for_agent_version(
            db,
            agent_version_id=version_id,
        )

    def transition_status(
        self,
        db: Session,
        *,
        deployment_id: UUID,
        target_status: DeploymentStatus,
        current_user: User,
        failure_reason: str | None = None,
    ) -> Deployment:
        deployment = self.get_deployment(
            db,
            deployment_id=deployment_id,
            current_user=current_user,
        )

        allowed_targets = self.ALLOWED_TRANSITIONS.get(
            deployment.status,
            set(),
        )

        if target_status not in allowed_targets:
            raise PlatformException(
                message=(
                    f"Deployment cannot transition from "
                    f"{deployment.status.value} to "
                    f"{target_status.value}"
                ),
                error_code="INVALID_DEPLOYMENT_TRANSITION",
                status_code=409,
            )

        if (
            target_status == DeploymentStatus.FAILED
            and not failure_reason
        ):
            raise PlatformException(
                message=(
                    "A failure reason is required when "
                    "marking a deployment as failed"
                ),
                error_code="DEPLOYMENT_FAILURE_REASON_REQUIRED",
                status_code=409,
            )

        normalized_failure_reason = (
            failure_reason.strip()
            if failure_reason is not None
            else None
        )

        deployment = self.deployment_repository.update_status(
            db,
            deployment=deployment,
            status=target_status,
            failure_reason=normalized_failure_reason,
        )

        db.commit()
        db.refresh(deployment)

        return deployment
