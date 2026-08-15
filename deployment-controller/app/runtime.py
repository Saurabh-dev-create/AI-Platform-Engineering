import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.repository import ClaimedDeployment


logger = logging.getLogger(__name__)


class RuntimeStatus(StrEnum):
    """
    Runtime-observed state independent of deployment DB state.
    """

    MATERIALIZED = "materialized"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass(frozen=True)
class RuntimeInstance:
    """
    Runtime-side representation of one Zevinq deployment.
    """

    deployment_id: UUID
    runtime_id: str
    status: RuntimeStatus
    message: str | None = None


class RuntimeAdapter(ABC):
    """
    Execution boundary used by the deployment controller.

    Implementations translate an immutable deployment snapshot
    into a concrete runtime instance.
    """

    @abstractmethod
    def materialize(
        self,
        deployment: ClaimedDeployment,
    ) -> RuntimeInstance:
        """
        Create the runtime representation for a deployment.
        """
        raise NotImplementedError


    @abstractmethod
    def start(
        self,
        deployment: ClaimedDeployment,
        instance: RuntimeInstance,
    ) -> RuntimeInstance:
        """
        Start the materialized runtime instance.
        """
        raise NotImplementedError


    @abstractmethod
    def observe(
        self,
        instance: RuntimeInstance,
    ) -> RuntimeInstance:
        """
        Return the current runtime-observed state.
        """
        raise NotImplementedError


    @abstractmethod
    def stop(
        self,
        instance: RuntimeInstance,
    ) -> RuntimeInstance:
        """
        Stop an existing runtime instance.
        """
        raise NotImplementedError


class SimulatedRuntime(RuntimeAdapter):
    """
    Runtime implementation used for control-plane validation.

    It exercises the complete runtime lifecycle without creating
    external infrastructure.
    """

    def materialize(
        self,
        deployment: ClaimedDeployment,
    ) -> RuntimeInstance:
        runtime_id = (
            f"simulated-{deployment.id}"
        )

        logger.info(
            "simulated_runtime_materialized "
            "deployment_id=%s "
            "runtime_id=%s",
            deployment.id,
            runtime_id,
        )

        return RuntimeInstance(
            deployment_id=deployment.id,
            runtime_id=runtime_id,
            status=RuntimeStatus.MATERIALIZED,
        )


    def start(
        self,
        deployment: ClaimedDeployment,
        instance: RuntimeInstance,
    ) -> RuntimeInstance:
        logger.info(
            "simulated_runtime_started "
            "deployment_id=%s "
            "runtime_id=%s "
            "agent_version_id=%s "
            "environment=%s "
            "strategy=%s",
            deployment.id,
            instance.runtime_id,
            deployment.agent_version_id,
            deployment.environment,
            deployment.strategy,
        )

        return RuntimeInstance(
            deployment_id=instance.deployment_id,
            runtime_id=instance.runtime_id,
            status=RuntimeStatus.RUNNING,
        )


    def observe(
        self,
        instance: RuntimeInstance,
    ) -> RuntimeInstance:
        return instance


    def stop(
        self,
        instance: RuntimeInstance,
    ) -> RuntimeInstance:
        logger.info(
            "simulated_runtime_stopped "
            "deployment_id=%s "
            "runtime_id=%s",
            instance.deployment_id,
            instance.runtime_id,
        )

        return RuntimeInstance(
            deployment_id=instance.deployment_id,
            runtime_id=instance.runtime_id,
            status=RuntimeStatus.STOPPED,
        )
