"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import MagicMock, patch

from docker.errors import DockerException

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.const import UnhealthyReason
from supervisor.resolution.evaluations.container import EvaluateContainer


def test_get_images(coresys: CoreSys):
    """Test getting images form docker."""
    container = EvaluateContainer(coresys)
    with patch(
        "supervisor.resolution.evaluations.container.EvaluateContainer._get_images",
        return_value=[MagicMock(tags=["test"])],
    ):

        images = container._get_images()
        assert images[0].tags[0] == "test"

    with patch("supervisor.docker.DockerAPI.images.list", side_effect=DockerException):
        images = container._get_images()
        assert not images


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    container = EvaluateContainer(coresys)
    coresys.core.state = CoreState.RUNNING

    assert container.reason not in coresys.resolution.unsupported
    assert UnhealthyReason.DOCKER not in coresys.resolution.unhealthy

    with patch(
        "supervisor.resolution.evaluations.container.EvaluateContainer._get_images",
        return_value=[
            "armhfbuild/watchtower:latest",
            "concerco/watchtowerv6:10.0.2",
            "containrrr/watchtower:1.1",
            "pyouroboros/ouroboros:1.4.3",
        ],
    ):
        await container()
        assert container.reason in coresys.resolution.unsupported
        assert UnhealthyReason.DOCKER in coresys.resolution.unhealthy

    assert coresys.resolution.evaluate.cached_images == {
        "armhfbuild/watchtower:latest",
        "concerco/watchtowerv6:10.0.2",
        "containrrr/watchtower:1.1",
        "pyouroboros/ouroboros:1.4.3",
    }

    with patch(
        "supervisor.resolution.evaluations.container.EvaluateContainer._get_images",
        return_value=[],
    ):
        await container()
        assert container.reason not in coresys.resolution.unsupported

    assert coresys.resolution.evaluate.cached_images == set()


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
            coresys.core.state = state
            await container()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await container()
            evaluate.assert_not_called()
            evaluate.reset_mock()
