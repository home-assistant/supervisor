"""Testing handling with CoreState."""

from supervisor.const import CoreState
from supervisor.coresys import CoreSys


def test_write_state(run_dir, coresys: CoreSys):
    """Test write corestate to /run/supervisor."""

    coresys.core.state = CoreState.RUNNING

    assert run_dir.read_text() == CoreState.RUNNING.value

    coresys.core.state = CoreState.SHUTDOWN

    assert run_dir.read_text() == CoreState.SHUTDOWN.value
