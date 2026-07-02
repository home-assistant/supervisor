"""Tests for EvaluateContainer."""

from unittest.mock import AsyncMock, MagicMock

import aiodocker
from aiodocker.containers import DockerContainer
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.const import IssueType
from supervisor.resolution.evaluations.container import EvaluateContainer


async def test_evaluate_container_list_timeout(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test evaluate returns False and logs on containers.list timeout, no corrupt issue."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.docker.containers.list.side_effect = TimeoutError()

    evaluation = EvaluateContainer(coresys)
    result = await evaluation.evaluate()

    assert result is False
    assert "Timeout while evaluating docker containers" in caplog.text
    # A timeout is not a sign of corrupt Docker; no issue should be created
    assert not any(
        issue.type == IssueType.CORRUPT_DOCKER for issue in coresys.resolution.issues
    )


async def test_evaluate_container_show_timeout(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test evaluate returns False and logs when container.show times out, no corrupt issue."""
    await coresys.core.set_state(CoreState.RUNNING)
    mock_container = MagicMock(spec=DockerContainer)
    mock_container.show = AsyncMock(side_effect=TimeoutError())
    coresys.docker.containers.list.return_value = [mock_container]

    evaluation = EvaluateContainer(coresys)
    result = await evaluation.evaluate()

    assert result is False
    assert "Timeout while evaluating docker containers" in caplog.text
    assert not any(
        issue.type == IssueType.CORRUPT_DOCKER for issue in coresys.resolution.issues
    )


async def test_evaluate_container_docker_error_creates_corrupt_issue(
    coresys: CoreSys,
):
    """Test evaluate creates CORRUPT_DOCKER issue on DockerError (original behavior)."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.docker.containers.list.side_effect = aiodocker.DockerError(
        500, {"message": "overlayfs error"}
    )

    evaluation = EvaluateContainer(coresys)
    result = await evaluation.evaluate()

    assert result is False
    assert any(
        issue.type == IssueType.CORRUPT_DOCKER for issue in coresys.resolution.issues
    )
