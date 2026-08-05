from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies.database import get_db_session
from app.models.user import User
from app.repositories.agent_repository import AgentRepository
from app.repositories.agent_version_repository import AgentVersionRepository
from app.repositories.deployment_repository import DeploymentRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.team_membership_repository import (
    TeamMembershipRepository,
)
from app.schemas.deployment import (
    DeploymentCreate,
    DeploymentResponse,
)
from app.services.deployment_service import DeploymentService


router = APIRouter(
    tags=["Deployments"],
)


def build_deployment_service() -> DeploymentService:
    return DeploymentService(
        DeploymentRepository(),
        AgentVersionRepository(),
        AgentRepository(),
        ProjectRepository(),
        TeamMembershipRepository(),
    )


@router.post(
    "/deployments",
    response_model=DeploymentResponse,
    status_code=201,
)
def create_deployment(
    deployment_data: DeploymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> DeploymentResponse:
    service = build_deployment_service()

    deployment = service.create_deployment(
        db,
        current_user=current_user,
        deployment_data=deployment_data,
    )

    return DeploymentResponse.model_validate(deployment)


@router.get(
    "/deployments/{deployment_id}",
    response_model=DeploymentResponse,
)
def get_deployment(
    deployment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> DeploymentResponse:
    service = build_deployment_service()

    deployment = service.get_deployment(
        db,
        deployment_id=deployment_id,
        current_user=current_user,
    )

    return DeploymentResponse.model_validate(deployment)


@router.get(
    "/agent-versions/{version_id}/deployments",
    response_model=list[DeploymentResponse],
)
def list_deployments_for_version(
    version_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[DeploymentResponse]:
    service = build_deployment_service()

    deployments = service.list_deployments_for_version(
        db,
        version_id=version_id,
        current_user=current_user,
    )

    return [
        DeploymentResponse.model_validate(deployment)
        for deployment in deployments
    ]
