from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies.database import get_db_session
from app.models.user import User
from app.repositories.agent_repository import AgentRepository
from app.repositories.agent_version_repository import (
    AgentVersionRepository,
)
from app.repositories.project_repository import ProjectRepository
from app.repositories.team_membership_repository import (
    TeamMembershipRepository,
)
from app.schemas.agent_version import (
    AgentVersionCreate,
    AgentVersionResponse,
)
from app.services.agent_version_service import AgentVersionService


router = APIRouter(
    tags=["Agent Versions"],
)


def build_agent_version_service() -> AgentVersionService:
    return AgentVersionService(
        AgentVersionRepository(),
        AgentRepository(),
        ProjectRepository(),
        TeamMembershipRepository(),
    )


@router.post(
    "/agents/{agent_id}/versions",
    response_model=AgentVersionResponse,
    status_code=201,
)
def create_agent_version(
    agent_id: UUID,
    version_data: AgentVersionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> AgentVersionResponse:
    service = build_agent_version_service()

    version = service.create_version(
        db,
        agent_id=agent_id,
        current_user=current_user,
        version_data=version_data,
    )

    return AgentVersionResponse.model_validate(version)


@router.get(
    "/agents/{agent_id}/versions",
    response_model=list[AgentVersionResponse],
)
def list_agent_versions(
    agent_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[AgentVersionResponse]:
    service = build_agent_version_service()

    versions = service.list_versions(
        db,
        agent_id=agent_id,
        current_user=current_user,
    )

    return [
        AgentVersionResponse.model_validate(version)
        for version in versions
    ]


@router.get(
    "/agent-versions/{version_id}",
    response_model=AgentVersionResponse,
)
def get_agent_version(
    version_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> AgentVersionResponse:
    service = build_agent_version_service()

    version = service.get_version(
        db,
        version_id=version_id,
        current_user=current_user,
    )

    return AgentVersionResponse.model_validate(version)
@router.post(
    "/agent-versions/{version_id}/publish",
    response_model=AgentVersionResponse,
)
def publish_agent_version(
    version_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> AgentVersionResponse:
    service = build_agent_version_service()

    version = service.publish_version(
        db,
        version_id=version_id,
        current_user=current_user,
    )

    return AgentVersionResponse.model_validate(version)


@router.post(
    "/agent-versions/{version_id}/deprecate",
    response_model=AgentVersionResponse,
)
def deprecate_agent_version(
    version_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> AgentVersionResponse:
    service = build_agent_version_service()

    version = service.deprecate_version(
        db,
        version_id=version_id,
        current_user=current_user,
    )

    return AgentVersionResponse.model_validate(version)
