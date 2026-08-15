import logging
from abc import ABC, abstractmethod

from app.repository import ClaimedDeployment


logger = logging.getLogger(__name__)


class RuntimeAdapter(ABC):
    """
    Execution boundary used by the deployment controller.

    Runtime implementations are responsible for materializing
    an approved deployment into an actual runtime environment.
    """

    @abstractmethod
    def deploy(
        self,
        deployment: ClaimedDeployment,
    ) -> None:
        """
        Execute the deployment.

        Raise an exception when runtime execution fails.
        """
        raise NotImplementedError


class SimulatedRuntime(RuntimeAdapter):
    """
    Initial runtime adapter used to validate controller reconciliation.

    This implementation intentionally performs no external deployment.
    It will later be replaced by concrete runtime adapters such as
    KubernetesRuntime.
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
