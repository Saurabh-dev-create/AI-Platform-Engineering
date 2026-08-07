from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import PlanType
from app.models.team_entitlement import TeamEntitlement


class TeamEntitlementRepository:
    """
    Database access layer for workspace plan entitlements.
    """

    def get_by_team_id(
        self,
        db: Session,
        *,
        team_id: UUID,
    ) -> TeamEntitlement | None:
        statement = select(TeamEntitlement).where(
            TeamEntitlement.team_id == team_id,
        )

        return db.scalar(statement)

    def create_free(
        self,
        db: Session,
        *,
        team_id: UUID,
    ) -> TeamEntitlement:
        entitlement = TeamEntitlement(
            team_id=team_id,
            plan=PlanType.FREE,
            max_projects=2,
            max_agents=3,
            max_members=1,
            allow_runtime_execution=False,
            allow_paid_provider_usage=False,
            allow_staging_deployments=False,
            allow_production_deployments=False,
        )

        db.add(entitlement)
        db.flush()
        db.refresh(entitlement)

        return entitlement
