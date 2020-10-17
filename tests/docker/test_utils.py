"""Test Docker Utils."""
import time
from unittest.mock import MagicMock, call

from supervisor.docker.utils import PullProgress
from supervisor.utils import JobMonitor, job_monitor
from tests.common import load_json_fixture


def test_pull_progress():
    """Test PullProgress class."""

    job = JobMonitor(None)
    job.send_progress = MagicMock()
    job_monitor.set(job)

    pull = PullProgress("test-object", 0.01)
    pull.start()
    for line in _pull_log_stream():
        pull.process_log(line)
    pull.done()

    assert 5 <= len(job.send_progress.mock_calls) <= 7

    first = job.send_progress.mock_calls[0]
    last = job.send_progress.mock_calls[-1]
    assert first == call("test-object", None, None)
    assert last == call("test-object", 1.0, 1.0)


def _pull_log_stream():
    pull_log = load_json_fixture("docker-pull-log.json")
    for log in pull_log:
        time.sleep(0.0001)
        yield log
