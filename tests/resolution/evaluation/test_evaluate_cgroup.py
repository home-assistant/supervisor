"""Test evaluation base."""

# pylint: disable=import-error
from unittest.mock import patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.cgroup import (
    CGROUP_V1_VERSION,
    CGROUP_V2_VERSION,
    EvaluateCGroupVersion,
)


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    cgroup_version = EvaluateCGroupVersion(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    assert cgroup_version.reason not in coresys.resolution.unsupported

    coresys.docker.info.cgroup = "unsupported"
    await cgroup_version()
    assert cgroup_version.reason in coresys.resolution.unsupported
    coresys.resolution.unsupported.clear()

    coresys.docker.info.cgroup = CGROUP_V2_VERSION
    await cgroup_version()
    assert cgroup_version.reason not in coresys.resolution.unsupported
    coresys.resolution.unsupported.clear()

    coresys.docker.info.cgroup = CGROUP_V1_VERSION
    await cgroup_version()
    assert cgroup_version.reason not in coresys.resolution.unsupported


async def test_evaluation_os_available(coresys: CoreSys, os_available):
    """Test evaluation with OS available."""
    cgroup_version = EvaluateCGroupVersion(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    coresys.docker.info.cgroup = CGROUP_V2_VERSION
    await cgroup_version()
    assert cgroup_version.reason not in coresys.resolution.unsupported

    coresys.docker.info.cgroup = CGROUP_V1_VERSION
    await cgroup_version()
    assert cgroup_version.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    cgroup_version = EvaluateCGroupVersion(coresys)
    should_run = cgroup_version.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.cgroup.EvaluateCGroupVersion.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            await coresys.core.set_state(state)
            await cgroup_version()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await cgroup_version()
            evaluate.assert_not_called()
            evaluate.reset_mock()
