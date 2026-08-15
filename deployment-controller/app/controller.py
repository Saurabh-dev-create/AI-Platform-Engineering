import logging

from sqlalchemy.orm import Session

from app.repository import DeploymentRepository
from app.runtime import (
    RuntimeAdapter,
    RuntimeStatus,
)


logger = logging.getLogger(__name__)


class DeploymentController:
    """
    Reconcile approved deployment intent into runtime state.
    """

    def __init__(
        self,
        repository: DeploymentRepository,
        runtime: RuntimeAdapter,
    ) -> None:
        self.repository = repository
        self.runtime = runtime


    def reconcile_once(
        self,
        db: Session,
    ) -> bool:
        """
        Reconcile at most one approved deployment.

        Return True when work was claimed, otherwise False.
        """

        deployment = self.repository.claim_next_approved(db)

        if deployment is None:
            db.rollback()
            return False

        # Commit the atomic claim before external runtime work.
        db.commit()

        logger.info(
            "deployment_claimed deployment_id=%s",
            deployment.id,
        )

        try:
            instance = self.runtime.materialize(
                deployment
            )

            instance = self.runtime.start(
                deployment,
                instance,
            )

            observed = self.runtime.observe(
                instance
            )

            if observed.status != RuntimeStatus.RUNNING:
                raise RuntimeError(
                    "Runtime did not reach running state: "
                    f"{observed.status}"
                )
        except Exception as exc:
            logger.exception(
                "deployment_runtime_failed deployment_id=%s",
                deployment.id,
            )

            self.repository.mark_failed(
                db,
                deployment_id=deployment.id,
                failure_reason=str(exc),
            )
            db.commit()

            return True

        self.repository.mark_running(
            db,
            deployment_id=deployment.id,
        )
        db.commit()

        logger.info(
            "deployment_running deployment_id=%s",
            deployment.id,
        )

        return True
