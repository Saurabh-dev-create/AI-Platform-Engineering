import logging
import time

from app.config import settings
from app.controller import DeploymentController
from app.database import SessionLocal
from app.repository import DeploymentRepository
from app.runtime import SimulatedRuntime


logging.basicConfig(
    level=getattr(
        logging,
        settings.log_level.upper(),
        logging.INFO,
    ),
    format=(
        "%(asctime)s %(levelname)s "
        "%(name)s %(message)s"
    ),
)

logger = logging.getLogger(__name__)


def main() -> None:
    repository = DeploymentRepository()
    runtime = SimulatedRuntime()

    controller = DeploymentController(
        repository,
        runtime,
    )

    logger.info(
        "deployment_controller_started "
        "poll_interval_seconds=%s "
        "batch_size=%s "
        "stale_after_seconds=%s",
        settings.poll_interval_seconds,
        settings.batch_size,
        settings.stale_after_seconds,
    )

    while True:
        processed = 0

        with SessionLocal() as db:
            try:
                stale_ids = repository.fail_stale_deploying(
                    db,
                    stale_after_seconds=(
                        settings.stale_after_seconds
                    ),
                    limit=settings.batch_size,
                )

                db.commit()

                for deployment_id in stale_ids:
                    logger.warning(
                        "stale_deployment_failed "
                        "deployment_id=%s",
                        deployment_id,
                    )
            except Exception:
                db.rollback()

                logger.exception(
                    "stale_deployment_recovery_failed"
                )

        for _ in range(settings.batch_size):
            with SessionLocal() as db:
                try:
                    claimed = controller.reconcile_once(db)
                except Exception:
                    db.rollback()

                    logger.exception(
                        "deployment_reconciliation_failed"
                    )

                    break

            if not claimed:
                break

            processed += 1

        if processed == 0:
            time.sleep(
                settings.poll_interval_seconds
            )


if __name__ == "__main__":
    main()
