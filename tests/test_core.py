"""Testing handling with CoreState."""

from supervisor.const import SupervisorState
from supervisor.coresys import CoreSys


def test_write_state(run_dir, coresys: CoreSys):
    """Test write corestate to /run/supervisor."""

    coresys.core.state = SupervisorState.RUNNING

    assert run_dir.read_text() == SupervisorState.RUNNING.value

    coresys.core.state = SupervisorState.SHUTDOWN

    assert run_dir.read_text() == SupervisorState.SHUTDOWN.value
