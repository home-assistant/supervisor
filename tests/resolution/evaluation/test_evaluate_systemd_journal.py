"""Test evaluation base."""

# pylint: disable=import-error,protected-access
from unittest.mock import MagicMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.evaluations.systemd_journal import EvaluateSystemdJournal


async def test_evaluation_supported(journald_gateway: MagicMock, coresys: CoreSys):
    """Test evaluation for supported system."""
    systemd_journal = EvaluateSystemdJournal(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    await systemd_journal()
    assert systemd_journal.reason not in coresys.resolution.unsupported


async def test_evaluation_unsupported(coresys: CoreSys):
    """Test evaluation for unsupported system."""
    systemd_journal = EvaluateSystemdJournal(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    with patch("supervisor.host.logs.SYSTEMD_JOURNAL_GATEWAYD_SOCKET") as socket:
        socket.is_socket.return_value = False
        await coresys.host.logs.post_init()
        await systemd_journal()

    assert systemd_journal.reason in coresys.resolution.unsupported


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
            await coresys.core.set_state(state)
            await systemd_journal()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await systemd_journal()
            evaluate.assert_not_called()
            evaluate.reset_mock()
