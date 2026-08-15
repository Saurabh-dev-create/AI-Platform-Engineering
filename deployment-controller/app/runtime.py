import logging

from app.repository import ClaimedDeployment


logger = logging.getLogger(__name__)


class SimulatedRuntime:
    """
    Initial runtime adapter for validating controller reconciliation.

    This adapter intentionally performs no external deployment yet.
    It will later be replaced by Kubernetes/GitOps runtime adapters.
    """

    def deploy(
        self,
        deployment: ClaimedDeployment,
    ) -> None:
        logger.info(
            "simulated deployment execution "
            "deployment_id=%s "
            "agent_version_id=%s "
            "environment=%s "
            "strategy=%s",
            deployment.id,
            deployment.agent_version_id,
            deployment.environment,
            deployment.strategy,
        )
