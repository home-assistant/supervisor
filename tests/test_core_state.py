"""Testing handling with CoreState."""
from pathlib import Path
from unittest.mock import patch

import pytest

from supervisor.const import CoreState

# pylint: disable=redefined-outer-name


@pytest.fixture
def run_dir(tmp_path):
    """Fixture to inject hassio env."""
    with patch("supervisor.core.RUN_SUPERVISOR_STATE") as mock_run:
        tmp_state = Path(tmp_path, "supervisor")
        mock_run.write_text = tmp_state.write_text
        yield tmp_state


def test_write_state(run_dir, coresys):
    """Test write corestate to /run/supervisor."""

    coresys.core.state = CoreState.RUNNING

    assert run_dir.read_text() == CoreState.RUNNING.value

    coresys.core.state = CoreState.SHUTDOWN

    assert run_dir.read_text() == CoreState.SHUTDOWN.value
