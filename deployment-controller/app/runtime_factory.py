from app.runtime import (
    RuntimeAdapter,
    SimulatedRuntime,
)


def build_runtime(
    runtime_name: str,
) -> RuntimeAdapter:
    """
    Build the configured deployment runtime adapter.
    """

    normalized_name = runtime_name.strip().lower()

    if normalized_name == "simulated":
        return SimulatedRuntime()

    raise ValueError(
        f"Unsupported deployment runtime: {runtime_name}"
    )
