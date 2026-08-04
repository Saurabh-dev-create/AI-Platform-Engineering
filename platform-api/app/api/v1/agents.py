from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies.database import get_db_session
from app.models.user import User
from app.repositories.agent_repository import AgentRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.team_membership_repository import (
    TeamMembershipRepository,
)
from app.schemas.agent import AgentCreate, AgentResponse
from app.services.agent_service import AgentService


router = APIRouter(
    tags=["Agents"],
)


def build_agent_service() -> AgentService:
    return AgentService(
        AgentRepository(),
        ProjectRepository(),
        TeamMembershipRepository(),
    )


@router.post(
    "/projects/{project_id}/agents",
    response_model=AgentResponse,
    status_code=201,
)
def create_agent(
    project_id: UUID,
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> AgentResponse:
    service = build_agent_service()

    agent = service.create_agent(
        db,
        project_id=project_id,
        current_user=current_user,
        agent_data=agent_data,
    )

    return AgentResponse.model_validate(agent)


@router.get(
    "/projects/{project_id}/agents",
    response_model=list[AgentResponse],
)
def list_agents(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[AgentResponse]:
    service = build_agent_service()

    agents = service.list_agents(
        db,
        project_id=project_id,
        current_user=current_user,
    )

    return [
        AgentResponse.model_validate(agent)
        for agent in agents
    ]


@router.get(
    "/agents/{agent_id}",
    response_model=AgentResponse,
)
def get_agent(
    agent_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> AgentResponse:
    service = build_agent_service()

    agent = service.get_agent(
        db,
        agent_id=agent_id,
        current_user=current_user,
    )

    return AgentResponse.model_validate(agent)
