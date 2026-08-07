from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies.database import get_db_session
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.repositories.team_membership_repository import (
    TeamMembershipRepository,
)
from app.repositories.team_entitlement_repository import (
    TeamEntitlementRepository,
)
from app.repositories.team_repository import TeamRepository
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project_service import ProjectService
from app.services.entitlement_service import EntitlementService


router = APIRouter(
    tags=["Projects"],
)


def build_project_service() -> ProjectService:
    return ProjectService(
        ProjectRepository(),
        TeamRepository(),
        TeamMembershipRepository(),
        EntitlementService(
            TeamEntitlementRepository(),
        ),
    )


@router.post(
    "/teams/{team_id}/projects",
    response_model=ProjectResponse,
    status_code=201,
)
def create_project(
    team_id: UUID,
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ProjectResponse:
    service = build_project_service()

    project = service.create_project(
        db,
        team_id=team_id,
        current_user=current_user,
        project_data=project_data,
    )

    return ProjectResponse.model_validate(project)


@router.get(
    "/teams/{team_id}/projects",
    response_model=list[ProjectResponse],
)
def list_projects(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[ProjectResponse]:
    service = build_project_service()

    projects = service.list_projects(
        db,
        team_id=team_id,
        current_user=current_user,
    )

    return [
        ProjectResponse.model_validate(project)
        for project in projects
    ]


@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ProjectResponse:
    service = build_project_service()

    project = service.get_project(
        db,
        project_id=project_id,
        current_user=current_user,
    )

    return ProjectResponse.model_validate(project)
