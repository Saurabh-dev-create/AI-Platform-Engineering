from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class ClaimedDeployment:
    id: UUID
    agent_version_id: UUID
    agent_id: UUID
    version_number: int
    environment: str
    strategy: str
    model_config: dict
    prompt_template: str | None
    runtime_config: dict
    tool_config: dict
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
                SELECT deployment.id
                FROM deployments AS deployment
                WHERE deployment.status = 'approved'
                ORDER BY deployment.created_at
                FOR UPDATE SKIP LOCKED
                LIMIT 1
            ),
            claimed_deployment AS (
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
            )
            SELECT
                claimed.id,
                claimed.agent_version_id,
                version.agent_id,
                version.version_number,
                claimed.environment,
                claimed.strategy,
                version.model_config,
                version.prompt_template,
                version.runtime_config,
                version.tool_config,
                claimed.requested_by_user_id
            FROM claimed_deployment AS claimed
            JOIN agent_versions AS version
                ON version.id = claimed.agent_version_id
            """
        )

        row = db.execute(statement).mappings().first()

        if row is None:
            return None

        return ClaimedDeployment(
            id=row["id"],
            agent_version_id=row["agent_version_id"],
            agent_id=row["agent_id"],
            version_number=row["version_number"],
            environment=row["environment"],
            strategy=row["strategy"],
            model_config=row["model_config"],
            prompt_template=row["prompt_template"],
            runtime_config=row["runtime_config"],
            tool_config=row["tool_config"],
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


    def fail_stale_deploying(
        self,
        db: Session,
        *,
        stale_after_seconds: int,
        limit: int = 20,
    ) -> list[UUID]:
        """
        Mark stale deploying records as failed.

        The controller deliberately does not automatically retry these
        deployments because external runtime execution may already have
        partially succeeded.
        """

        statement = text(
            """
            WITH stale_deployments AS (
                SELECT id
                FROM deployments
                WHERE
                    status = 'deploying'
                    AND updated_at < (
                        NOW()
                        - (
                            CAST(
                                :stale_after_seconds AS INTEGER
                            )
                            * INTERVAL '1 second'
                        )
                    )
                ORDER BY updated_at
                FOR UPDATE SKIP LOCKED
                LIMIT :limit
            )
            UPDATE deployments AS deployment
            SET
                status = 'failed',
                failure_reason = (
                    'Deployment controller timed out while '
                    'waiting for runtime completion'
                ),
                updated_at = NOW()
            FROM stale_deployments
            WHERE deployment.id = stale_deployments.id
            RETURNING deployment.id
            """
        )

        rows = db.execute(
            statement,
            {
                "stale_after_seconds":
                    stale_after_seconds,
                "limit": limit,
            },
        ).scalars().all()

        return list(rows)
