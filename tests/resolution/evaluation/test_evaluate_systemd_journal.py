"""Test evaluation base."""
# pylint: disable=import-error,protected-access
from unittest.mock import MagicMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.systemd_journal import EvaluateSystemdJournal


async def test_evaluation(coresys: CoreSys, journald_gateway: MagicMock):
    """Test evaluation."""
    systemd_journal = EvaluateSystemdJournal(coresys)
    coresys.core.state = CoreState.SETUP

    assert systemd_journal.reason not in coresys.resolution.unsupported

    with patch("supervisor.host.logs.Path.is_socket", return_value=False):
        await systemd_journal()
        assert systemd_journal.reason in coresys.resolution.unsupported

    coresys.host.supported_features.cache_clear()  # pylint: disable=no-member

    await systemd_journal()
    assert systemd_journal.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    systemd_journal = EvaluateSystemdJournal(coresys)
    should_run = systemd_journal.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.systemd_journal.EvaluateSystemdJournal.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            coresys.core.state = state
            await systemd_journal()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await systemd_journal()
            evaluate.assert_not_called()
            evaluate.reset_mock()
