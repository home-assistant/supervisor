"""Test Docker Utils."""

import json
import time

from supervisor.docker.utils import PullProgress

from tests.common import load_json_fixture


def test_pull_progress():
    """Test PullProgress class."""

    progress = PullProgress("test-object", 0.01)
    events = []
    for status in progress.process_log(_pull_log_stream()):
        events.append(status)

    assert 5 <= len(events) <= 7

    last = events.pop()
    assert (
        json.dumps(last) == '{"name": "test-object", '
        '"downloading": {"current": 293486178, "total": 293486178}, '
        '"extracting": {"current": 293486178, "total": 293486178}}'
    )


def _pull_log_stream():
    pull_log = load_json_fixture("docker-pull-log.json")
    for log in pull_log:
        time.sleep(0.0001)
        yield log
