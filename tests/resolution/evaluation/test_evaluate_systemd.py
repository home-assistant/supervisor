"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import MagicMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.systemd import EvaluateSystemd


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    systemd = EvaluateSystemd(coresys)
    coresys.core.state = CoreState.SETUP

    assert systemd.reason not in coresys.resolution.unsupported

    with patch(
        "supervisor.utils.gdbus.DBusCallWrapper",
        return_value=MagicMock(systemd=MagicMock(is_connected=False)),
    ):
        await systemd()
        assert systemd.reason in coresys.resolution.unsupported

    with patch(
        "supervisor.utils.gdbus.DBusCallWrapper",
        return_value=MagicMock(hostname=MagicMock(is_connected=False)),
    ):
        await systemd()
        assert systemd.reason in coresys.resolution.unsupported

    with patch(
        "supervisor.utils.gdbus.DBusCallWrapper",
        return_value=MagicMock(
            hostname=MagicMock(is_connected=True), systemd=MagicMock(is_connected=True)
        ),
    ):
        await systemd()
        assert systemd.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    systemd = EvaluateSystemd(coresys)
    should_run = systemd.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.systemd.EvaluateSystemd.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            coresys.core.state = state
            await systemd()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await systemd()
            evaluate.assert_not_called()
            evaluate.reset_mock()
