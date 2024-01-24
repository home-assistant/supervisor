"""Test evaluation of docker version."""

import random
from unittest.mock import patch

# pylint: disable=import-error,protected-access
from awesomeversion import AwesomeVersion

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.docker_version import EvaluateDockerVersion


async def test_evaluation_supported(coresys: CoreSys):
    """Test real evaluation with a current docker daemon."""
    docker_version = EvaluateDockerVersion(coresys)
    coresys.core.state = CoreState.INITIALIZE
    coresys.docker.info.version = AwesomeVersion("24.0.7")

    assert docker_version.reason not in coresys.resolution.unsupported

    await docker_version()

    assert docker_version.reason not in coresys.resolution.unsupported


async def test_evaluation_below_min_version(coresys: CoreSys):
    """Test handling of too-low docker versions."""
    docker_version = EvaluateDockerVersion(coresys)
    coresys.core.state = CoreState.INITIALIZE

    assert docker_version.reason not in coresys.resolution.unsupported

    minv = docker_version.min_supported_version
    coresys.docker.info.version = AwesomeVersion(f"{int(minv.major) - 1}.0.0")
    await docker_version()
    assert docker_version.reason in coresys.resolution.unsupported

    coresys.resolution.unsupported = []
    coresys.docker.info.version = AwesomeVersion(
        f"{minv.major}.{minv.minor}.{int(minv.patch) - 1}"
    )
    await docker_version()
    assert docker_version.reason in coresys.resolution.unsupported


async def test_evaluation_at_min_version(coresys: CoreSys):
    """Test handling of just-too-low docker versions."""
    docker_version = EvaluateDockerVersion(coresys)
    coresys.core.state = CoreState.INITIALIZE

    coresys.docker.info.version = docker_version.min_supported_version
    await docker_version()
    assert docker_version.reason not in coresys.resolution.unsupported


async def test_evaluation_known_broken_version(coresys: CoreSys):
    """Test handling of a known-bad docker versions."""
    docker_version = EvaluateDockerVersion(coresys)
    coresys.core.state = CoreState.INITIALIZE

    coresys.docker.info.version = random.choice(
        list(docker_version.broken_versions.keys())
    )
    await docker_version()
    assert docker_version.reason in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    docker_version = EvaluateDockerVersion(coresys)
    should_run = docker_version.states
    should_not_run = [state for state in CoreState if state not in should_run]
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
