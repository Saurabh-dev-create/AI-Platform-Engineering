from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import PlanType, TeamRole
from app.core.exceptions import (
    QuotaExceededException,
    ResourceConflictException,
)
from app.models.team import Team
from app.models.user import User
from app.repositories.team_membership_repository import (
    TeamMembershipRepository,
)
from app.repositories.team_repository import TeamRepository
from app.schemas.team import TeamCreate
from app.services.entitlement_service import EntitlementService
from uuid import UUID

from app.core.exceptions import ResourceNotFoundException

class TeamService:
    """
    Business logic for team lifecycle and tenant creation.
    """

    def __init__(
        self,
        team_repository: TeamRepository,
        membership_repository: TeamMembershipRepository,
        entitlement_service: EntitlementService,
    ) -> None:
        self.team_repository = team_repository
        self.membership_repository = membership_repository
        self.entitlement_service = entitlement_service

    def _require_workspace_creation_allowed(
        self,
        db: Session,
        *,
        current_user: User,
    ) -> None:
        owned_teams = self.team_repository.list_owned_by_user(
            db,
            user_id=current_user.id,
        )

        for team in owned_teams:
            entitlement = self.entitlement_service.require_for_team(
                db,
                team_id=team.id,
            )

            if entitlement.plan == PlanType.FREE:
                raise QuotaExceededException(
                    message=(
                        "Free accounts can own only one workspace"
                    ),
                    quota="workspaces",
                )

    def provision_team(
        self,
        db: Session,
        *,
        current_user: User,
        team_data: TeamCreate,
    ) -> Team:
        normalized_name = team_data.name.strip()
        normalized_slug = team_data.slug.lower()
        normalized_description = (
            team_data.description.strip()
            if team_data.description is not None
            else None
        )

        existing_team = self.team_repository.get_by_slug(
            db,
            normalized_slug,
        )

        if existing_team is not None:
            raise ResourceConflictException(
                resource="Team",
                field="slug",
                value=normalized_slug,
            )

        team = self.team_repository.create(
            db,
            name=normalized_name,
            slug=normalized_slug,
            description=normalized_description,
            created_by_user_id=current_user.id,
        )

        self.membership_repository.create(
            db,
            user_id=current_user.id,
            team_id=team.id,
            role=TeamRole.TEAM_ADMIN,
        )

        return team

    def create_team(
        self,
        db: Session,
        *,
        current_user: User,
        team_data: TeamCreate,
    ) -> Team:
        normalized_slug = team_data.slug.lower()

        self._require_workspace_creation_allowed(
            db,
            current_user=current_user,
        )

        try:
            team = self.provision_team(
                db,
                current_user=current_user,
                team_data=team_data,
            )

            db.commit()
            db.refresh(team)

            return team

        except IntegrityError as exc:
            db.rollback()

            raise ResourceConflictException(
                resource="Team",
                field="slug",
                value=normalized_slug,
            ) from exc

        except Exception:
            db.rollback()
            raise

    def get_team_for_user(
        self,
        db: Session,
        *,
        team_id: UUID,
        current_user: User,
    ) -> Team:
        team = self.team_repository.get_for_user_by_id(
            db,
            team_id=team_id,
            user_id=current_user.id,
        )

        if team is None:
            raise ResourceNotFoundException(
                resource="Team",
                resource_id=str(team_id),
            )

        return team
