"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import patch

from supervisor.const import SupervisorState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.docker_version import EvaluateDockerVersion


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    docker_version = EvaluateDockerVersion(coresys)
    coresys.core.state = SupervisorState.INITIALIZE

    assert docker_version.reason not in coresys.resolution.unsupported

    coresys.docker.info.supported_version = False
    await docker_version()
    assert docker_version.reason in coresys.resolution.unsupported

    coresys.docker.info.supported_version = True
    await docker_version()
    assert docker_version.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    docker_version = EvaluateDockerVersion(coresys)
    should_run = docker_version.states
    should_not_run = [state for state in SupervisorState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.docker_version.EvaluateDockerVersion.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            coresys.core.state = state
            await docker_version()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await docker_version()
            evaluate.assert_not_called()
            evaluate.reset_mock()
