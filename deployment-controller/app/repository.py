from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class ClaimedDeployment:
    id: UUID
    agent_version_id: UUID
    environment: str
    strategy: str
    requested_by_user_id: UUID | None


class DeploymentRepository:
    """
    Internal persistence operations used by the deployment controller.

    Controller work claiming is atomic so multiple replicas can safely
    poll the same PostgreSQL database.
    """

    def claim_next_approved(
        self,
        db: Session,
    ) -> ClaimedDeployment | None:
        statement = text(
            """
            WITH next_deployment AS (
                SELECT id
                FROM deployments
                WHERE status = 'approved'
                ORDER BY created_at
                FOR UPDATE SKIP LOCKED
                LIMIT 1
            )
            UPDATE deployments AS deployment
            SET
                status = 'deploying',
                updated_at = NOW()
            FROM next_deployment
            WHERE deployment.id = next_deployment.id
            RETURNING
                deployment.id,
                deployment.agent_version_id,
                deployment.environment,
                deployment.strategy,
                deployment.requested_by_user_id
            """
        )

        row = db.execute(statement).mappings().first()

        if row is None:
            return None

        return ClaimedDeployment(
            id=row["id"],
            agent_version_id=row["agent_version_id"],
            environment=row["environment"],
            strategy=row["strategy"],
            requested_by_user_id=row["requested_by_user_id"],
        )


    def mark_running(
        self,
        db: Session,
        *,
        deployment_id: UUID,
    ) -> None:
        statement = text(
            """
            UPDATE deployments
            SET
                status = 'running',
                updated_at = NOW()
            WHERE
                id = :deployment_id
                AND status = 'deploying'
            """
        )

        db.execute(
            statement,
            {
                "deployment_id": deployment_id,
            },
        )


    def mark_failed(
        self,
        db: Session,
        *,
        deployment_id: UUID,
        failure_reason: str,
    ) -> None:
        statement = text(
            """
            UPDATE deployments
            SET
                status = 'failed',
                failure_reason = :failure_reason,
                updated_at = NOW()
            WHERE
                id = :deployment_id
                AND status = 'deploying'
            """
        )

        db.execute(
            statement,
            {
                "deployment_id": deployment_id,
                "failure_reason": failure_reason,
            },
        )
