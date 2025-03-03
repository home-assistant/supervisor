"""Test evaluation base."""

# pylint: disable=import-error,protected-access
from unittest.mock import MagicMock, patch

from docker.errors import DockerException

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, UnhealthyReason
from supervisor.resolution.data import Issue
from supervisor.resolution.evaluations.container import EvaluateContainer


def _make_image_attr(image: str) -> MagicMock:
    out = MagicMock()
    out.attrs = {
        "Config": {
            "Image": image,
        },
    }
    return out


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    container = EvaluateContainer(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    assert container.reason not in coresys.resolution.unsupported
    assert UnhealthyReason.DOCKER not in coresys.resolution.unhealthy

    coresys.docker.containers.list.return_value = [
        _make_image_attr("armhfbuild/watchtower:latest"),
        _make_image_attr("concerco/watchtowerv6:10.0.2"),
        _make_image_attr("containrrr/watchtower:1.1"),
        _make_image_attr("pyouroboros/ouroboros:1.4.3"),
    ]
    await container()
    assert container.reason in coresys.resolution.unsupported
    assert UnhealthyReason.DOCKER in coresys.resolution.unhealthy

    assert coresys.resolution.evaluate.cached_images == {
        "armhfbuild/watchtower:latest",
        "concerco/watchtowerv6:10.0.2",
        "containrrr/watchtower:1.1",
        "pyouroboros/ouroboros:1.4.3",
    }

    coresys.docker.containers.list.return_value = []
    await container()
    assert container.reason not in coresys.resolution.unsupported

    assert coresys.resolution.evaluate.cached_images == set()


async def test_corrupt_docker(coresys: CoreSys):
    """Test corrupt docker issue."""
    container = EvaluateContainer(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    corrupt_docker = Issue(IssueType.CORRUPT_DOCKER, ContextType.SYSTEM)
    assert corrupt_docker not in coresys.resolution.issues

    coresys.docker.containers.list.side_effect = DockerException
    await container()
    assert corrupt_docker in coresys.resolution.issues


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    container = EvaluateContainer(coresys)
    should_run = container.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.container.EvaluateContainer.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            await coresys.core.set_state(state)
            await container()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await container()
            evaluate.assert_not_called()
            evaluate.reset_mock()
