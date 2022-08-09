"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.docker_configuration import (
    EXPECTED_LOGGING,
    EXPECTED_STORAGE,
    EvaluateDockerConfiguration,
)


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    docker_configuration = EvaluateDockerConfiguration(coresys)
    coresys.core.state = CoreState.INITIALIZE

    assert docker_configuration.reason not in coresys.resolution.unsupported

    coresys.docker.info.storage = "unsupported"
    coresys.docker.info.logging = EXPECTED_LOGGING
    await docker_configuration()
    assert docker_configuration.reason in coresys.resolution.unsupported
    coresys.resolution.unsupported.clear()

    coresys.docker.info.storage = EXPECTED_STORAGE
    coresys.docker.info.logging = "unsupported"
    await docker_configuration()
    assert docker_configuration.reason in coresys.resolution.unsupported
    coresys.resolution.unsupported.clear()

    coresys.docker.info.storage = EXPECTED_STORAGE
    coresys.docker.info.logging = EXPECTED_LOGGING
    await docker_configuration()
    assert docker_configuration.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    docker_configuration = EvaluateDockerConfiguration(coresys)
    should_run = docker_configuration.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.docker_configuration.EvaluateDockerConfiguration.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            coresys.core.state = state
            await docker_configuration()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await docker_configuration()
            evaluate.assert_not_called()
            evaluate.reset_mock()
