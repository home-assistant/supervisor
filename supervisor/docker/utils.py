"""Utils for Docker."""
import time


class PullProgress:
    """Docker pull log progress listener."""

    def __init__(self, name: str, sleep=1.0) -> None:
        """Initialize pull log listener."""
        self._name = name
        self._sleep = sleep
        self._next_push = 0
        self._downloading = Status()
        self._extracting = Status()

    def status(self):
        """Get pull status."""
        return {
            "name": self._name,
            "downloading": self._downloading.get(),
            "extracting": self._extracting.get(),
        }

    def done(self):
        """Mark current pull as done and send this info to HA Core."""
        self._downloading.done_all()
        self._extracting.done_all()
        return self.status()

    def process_log(self, pull_log):
        """Process pull log and yield current status."""
        for msg in pull_log:
            self._update(msg)
            if self._next_push < time.time():
                self._next_push = time.time() + self._sleep
                yield self.status()
        yield self.done()

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
        """Return the current status as dict."""
        return {
            "current": sum(self._current.values()),
            "total": sum(self._total.values()),
        }
