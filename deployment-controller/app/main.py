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
        "batch_size=%s",
        settings.poll_interval_seconds,
        settings.batch_size,
    )

    while True:
        processed = 0

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
