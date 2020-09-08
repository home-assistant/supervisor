"""Testing handling with CoreState."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from supervisor.const import CoreState


@pytest.fixture
def run_dir():
    """Fixture to inject hassio env."""
    with patch(
        "supervisor.core.RUN_SUPERVISOR_STATE"
    ) as mock_run, TemporaryDirectory() as tmp_run:
        tmp_state = Path(tmp_run, "supervisor")
        mock_run.write_text = tmp_state.write_text
        yield tmp_state


def test_write_state(run_dir, coresys):
    """Test write corestate to /run/supervisor."""

    coresys.core.state = CoreState.RUNNING

    assert run_dir.read_text() == CoreState.RUNNING.value

    coresys.core.state = CoreState.SHUTDOWN

    assert run_dir.read_text() == CoreState.SHUTDOWN.value
