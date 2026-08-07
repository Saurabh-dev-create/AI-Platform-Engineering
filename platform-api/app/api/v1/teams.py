from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies.database import get_db_session
from app.models.user import User
from app.repositories.team_membership_repository import (
    TeamMembershipRepository,
)
from app.repositories.team_entitlement_repository import (
    TeamEntitlementRepository,
)
from app.repositories.team_repository import TeamRepository
from app.schemas.team import TeamCreate, TeamResponse
from app.services.team_service import TeamService
from uuid import UUID


from app.repositories.user_repository import UserRepository
from app.schemas.team_membership import (
    TeamMemberAdd,
    TeamMemberRoleUpdate,
    TeamMembershipResponse,
)
from app.services.team_membership_service import (
    TeamMembershipService,
)
from app.services.entitlement_service import EntitlementService

router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
)


@router.post(
    "",
    response_model=TeamResponse,
    status_code=201,
)
def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> TeamResponse:
    service = TeamService(
        TeamRepository(),
        TeamMembershipRepository(),
        EntitlementService(
            TeamEntitlementRepository(),
        ),
    )

    team = service.create_team(
        db,
        current_user=current_user,
        team_data=team_data,
    )

    return TeamResponse.model_validate(team)
@router.get(
    "",
    response_model=list[TeamResponse],
)
def list_my_teams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[TeamResponse]:
    repository = TeamRepository()

    teams = repository.list_for_user(
        db,
        current_user.id,
    )

    return [
        TeamResponse.model_validate(team)
        for team in teams
    
    ]
@router.get(
    "/{team_id}",
    response_model=TeamResponse,
)
def get_team(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> TeamResponse:
    service = TeamService(
        TeamRepository(),
        TeamMembershipRepository(),
        EntitlementService(
            TeamEntitlementRepository(),
        ),
    )

    team = service.get_team_for_user(
        db,
        team_id=team_id,
        current_user=current_user,
    )

    return TeamResponse.model_validate(team)
@router.post(
    "/{team_id}/members",
    response_model=TeamMembershipResponse,
    status_code=201,
)
def add_team_member(
    team_id: UUID,
    member_data: TeamMemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> TeamMembershipResponse:
    service = TeamMembershipService(
        TeamRepository(),
        TeamMembershipRepository(),
        UserRepository(),
        EntitlementService(
            TeamEntitlementRepository(),
        ),
    )

    membership = service.add_member(
        db,
        team_id=team_id,
        current_user=current_user,
        member_data=member_data,
    )

    return TeamMembershipResponse.model_validate(membership)


@router.get(
    "/{team_id}/members",
    response_model=list[TeamMembershipResponse],
)
def list_team_members(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[TeamMembershipResponse]:
    service = TeamMembershipService(
        TeamRepository(),
        TeamMembershipRepository(),
        UserRepository(),
        EntitlementService(
            TeamEntitlementRepository(),
        ),
    )

    memberships = service.list_members(
        db,
        team_id=team_id,
        current_user=current_user,
    )

    return [
        TeamMembershipResponse.model_validate(membership)
        for membership in memberships
    ]


@router.patch(
    "/{team_id}/members/{target_user_id}",
    response_model=TeamMembershipResponse,
)
def update_team_member_role(
    team_id: UUID,
    target_user_id: UUID,
    role_data: TeamMemberRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> TeamMembershipResponse:
    service = TeamMembershipService(
        TeamRepository(),
        TeamMembershipRepository(),
        UserRepository(),
        EntitlementService(
            TeamEntitlementRepository(),
        ),
    )

    membership = service.update_member_role(
        db,
        team_id=team_id,
        target_user_id=target_user_id,
        current_user=current_user,
        role_data=role_data,
    )

    return TeamMembershipResponse.model_validate(membership)


@router.delete(
    "/{team_id}/members/{target_user_id}",
    status_code=204,
)
def remove_team_member(
    team_id: UUID,
    target_user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> None:
    service = TeamMembershipService(
        TeamRepository(),
        TeamMembershipRepository(),
        UserRepository(),
        EntitlementService(
            TeamEntitlementRepository(),
        ),
    )

    service.remove_member(
        db,
        team_id=team_id,
        target_user_id=target_user_id,
        current_user=current_user,
    )
