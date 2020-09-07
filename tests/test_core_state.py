"""Testing handling with CoreState."""

from supervisor.const import RUN_SUPERVISOR_STATE, CoreState


def test_write_state(coresys):
    """Test write corestate to /run/supervisor."""

    coresys.core.state = CoreState.RUNNING

    assert RUN_SUPERVISOR_STATE.read_text() == CoreState.RUNNING.value

    coresys.core.state = CoreState.SHUTDOWN

    assert RUN_SUPERVISOR_STATE.read_text() == CoreState.SHUTDOWN.value
