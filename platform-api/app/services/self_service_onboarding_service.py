from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.schemas.team import TeamCreate
from app.services.auth_service import AuthService
from app.services.entitlement_service import EntitlementService
from app.services.team_service import TeamService


class SelfServiceOnboardingService:
    """
    Orchestrate public self-service Free account provisioning.

    Registration creates the user, personal workspace,
    administrator membership, and Free entitlement in one
    database transaction.
    """

    def __init__(
        self,
        auth_service: AuthService,
        team_service: TeamService,
        entitlement_service: EntitlementService,
    ) -> None:
        self.auth_service = auth_service
        self.team_service = team_service
        self.entitlement_service = entitlement_service

    def register_free_user(
        self,
        db: Session,
        registration: RegisterRequest,
    ) -> User:
        try:
            user = self.auth_service.provision_user(
                db,
                registration,
            )

            workspace_name = (
                f"{user.full_name}'s Workspace"
            )

            workspace_slug = (
                f"workspace-{user.id}"
            )

            workspace = self.team_service.provision_team(
                db,
                current_user=user,
                team_data=TeamCreate(
                    name=workspace_name,
                    slug=workspace_slug,
                    description=(
                        "Personal Zevinq Free workspace."
                    ),
                ),
            )

            self.entitlement_service.create_free_entitlement(
                db,
                team_id=workspace.id,
            )

            db.commit()
            db.refresh(user)

            return user

        except Exception:
            db.rollback()
            raise
