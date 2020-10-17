"""Utils for Docker."""
import time

from ..utils import job_monitor


class PullProgress:
    """Docker pull log progress listener."""

    def __init__(self, name: str, sleep=1.0) -> None:
        """Initialize pull log listener."""
        self._name = name
        self._sleep = sleep
        self._next_push = 0
        self._downloading = Status()
        self._extracting = Status()
        self._job_monitor = job_monitor.get()

    def start(self):
        """Send progress on start."""
        self._next_push = time.time()
        self._send_progress()

    def process_log(self, line):
        """Process pull log and yield current status."""
        self._update(line)
        now = time.time()
        if self._next_push < now:
            self._next_push = now + self._sleep
            self._send_progress()

    def done(self):
        """Mark current pull as done and send this info to HA Core."""
        self._downloading.done_all()
        self._extracting.done_all()
        self._send_progress()

    def _send_progress(self):
        if self._job_monitor:
            self._job_monitor.send_progress(
                self._name,
                self._extracting.get(),
                self._downloading.get(),
            )

    def _update(self, data):
        try:
            layer_id = data["id"]
            detail = data["progressDetail"]
            if data["status"] == "Pulling fs layer":
                # unknown layer size, assume 100MB
                self._downloading.update(layer_id, 0, 100e6)
                self._extracting.update(layer_id, 0, 100e6)
            if data["status"] == "Downloading":
                self._downloading.update(layer_id, detail["current"], detail["total"])
                self._extracting.update(layer_id, 0, detail["total"])
            if data["status"] == "Extracting":
                self._downloading.done(layer_id)
                self._extracting.update(layer_id, detail["current"], detail["total"])
            if data["status"] == "Pull complete":
                self._downloading.done(layer_id)
                self._extracting.done(layer_id)
        except KeyError:
            pass


class Status:
    """Docker image status object."""

    def __init__(self):
        """Initialize status object."""
        self._current = {}
        self._total = {}

    def update(self, layer_id, current, total):
        """Update one layer status."""
        self._current[layer_id] = current
        self._total[layer_id] = total

    def done(self, layer_id):
        """Mark one layer as done."""
        if layer_id in self._total:
            self._current[layer_id] = self._total[layer_id]

    def done_all(self):
        """Mark image as done."""
        if len(self._total) == 0:
            self.update("id", 1, 1)
        for layer_id in self._total:
            self._current[layer_id] = self._total[layer_id]

    def get(self):
        """Return the current status."""
        total = sum(self._total.values())
        if total == 0:
            return None
        return sum(self._current.values()) / total
