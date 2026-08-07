from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import (
    PlatformException,
    QuotaExceededException,
)
from app.models.team_entitlement import TeamEntitlement
from app.repositories.team_entitlement_repository import (
    TeamEntitlementRepository,
)


class EntitlementService:
    """
    Enforce workspace plan limits and cost guardrails.
    """

    def __init__(
        self,
        entitlement_repository: TeamEntitlementRepository,
    ) -> None:
        self.entitlement_repository = entitlement_repository

    def create_free_entitlement(
        self,
        db: Session,
        *,
        team_id: UUID,
    ) -> TeamEntitlement:
        return self.entitlement_repository.create_free(
            db,
            team_id=team_id,
        )

    def require_for_team(
        self,
        db: Session,
        *,
        team_id: UUID,
    ) -> TeamEntitlement:
        entitlement = self.entitlement_repository.get_by_team_id(
            db,
            team_id=team_id,
        )

        if entitlement is None:
            raise PlatformException(
                message="Workspace entitlement is required",
                error_code="ENTITLEMENT_REQUIRED",
                status_code=403,
            )

        return entitlement

    def require_project_capacity(
        self,
        entitlement: TeamEntitlement,
        *,
        current_projects: int,
    ) -> None:
        if current_projects >= entitlement.max_projects:
            raise QuotaExceededException(
                message=(
                    "Workspace project quota has been reached"
                ),
                quota="projects",
            )

    def require_agent_capacity(
        self,
        entitlement: TeamEntitlement,
        *,
        current_agents: int,
    ) -> None:
        if current_agents >= entitlement.max_agents:
            raise QuotaExceededException(
                message=(
                    "Workspace agent quota has been reached"
                ),
                quota="agents",
            )

    def require_member_capacity(
        self,
        entitlement: TeamEntitlement,
        *,
        current_members: int,
    ) -> None:
        if current_members >= entitlement.max_members:
            raise QuotaExceededException(
                message=(
                    "Workspace member quota has been reached"
                ),
                quota="members",
            )

    def require_runtime_execution(
        self,
        entitlement: TeamEntitlement,
    ) -> None:
        if not entitlement.allow_runtime_execution:
            raise QuotaExceededException(
                message=(
                    "Runtime execution is not available "
                    "for this workspace plan"
                ),
                quota="runtime_execution",
            )

    def require_paid_provider_usage(
        self,
        entitlement: TeamEntitlement,
    ) -> None:
        if not entitlement.allow_paid_provider_usage:
            raise QuotaExceededException(
                message=(
                    "Paid provider usage is not available "
                    "for this workspace plan"
                ),
                quota="paid_provider_usage",
            )

    def require_staging_deployment(
        self,
        entitlement: TeamEntitlement,
    ) -> None:
        if not entitlement.allow_staging_deployments:
            raise QuotaExceededException(
                message=(
                    "Staging deployments are not available "
                    "for this workspace plan"
                ),
                quota="staging_deployments",
            )

    def require_production_deployment(
        self,
        entitlement: TeamEntitlement,
    ) -> None:
        if not entitlement.allow_production_deployments:
            raise QuotaExceededException(
                message=(
                    "Production deployments are not available "
                    "for this workspace plan"
                ),
                quota="production_deployments",
            )
