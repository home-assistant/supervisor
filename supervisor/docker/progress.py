import asyncio
import time
from contextlib import suppress

import docker

from ..coresys import CoreSysAttributes
from ..exceptions import HomeAssistantAPIError


def pull_with_progress(interface: CoreSysAttributes, image, tag):
    progress = PullProgress(interface)
    try:
        progress.send_event()
        pull_log = interface.sys_docker.api.pull(image, tag, stream=True, decode=True)
        progress.watch_log(pull_log)

        return interface.sys_docker.images.get(
            "{0}{2}{1}".format(image, tag, "@" if tag.startswith("sha256:") else ":")
        )
    except docker.errors.APIError as err:
        progress.done()
        raise err


class Status:
    def __init__(self):
        self._current = {}
        self._total = {}

    def update(self, layer_id, current, total):
        self._current[layer_id] = current
        self._total[layer_id] = total

    def done(self, layer_id):
        if layer_id in self._total:
            self._current[layer_id] = self._total[layer_id]

    def done_all(self):
        if len(self._total) == 0:
            self.update("id", 1, 1)
        for layer_id in self._total:
            self._current[layer_id] = self._total[layer_id]

    def current(self):
        return sum(self._current.values())

    def total(self):
        return sum(self._total.values())


class PullProgress:
    def __init__(self, interface: CoreSysAttributes, sleep=1.0) -> None:
        super().__init__()
        self._interface = interface
        self._sleep = sleep
        self._next_push = 0
        self._download = Status()
        self._extract = Status()

    def send_event(self):
        self._next_push = time.time() + self._sleep
        asyncio.run_coroutine_threadsafe(
            self.async_send_event(self.status()), self._interface.sys_loop,
        )

    def done(self):
        self._download.done_all()
        self._extract.done_all()
        self.send_event()

    async def async_send_event(self, status) -> None:
        with suppress(HomeAssistantAPIError):
            async with self._interface.sys_homeassistant.make_request(
                "post", "api/events/hassio_progress", json=status, timeout=2,
            ):
                pass

    def watch_log(self, pull_log):
        for msg in pull_log:
            self.update(msg)
            if self._next_push < time.time():
                self.send_event()
        self.done()

    def update(self, data):
        try:
            layer_id = data["id"]
            detail = data["progressDetail"]
            if data["status"] == "Pulling fs layer":
                # unknown layer size, assume 100MB
                self._download.update(layer_id, 0, 100e6)
                self._extract.update(layer_id, 0, 100e6)
            if data["status"] == "Downloading":
                self._download.update(layer_id, detail["current"], detail["total"])
                self._extract.update(layer_id, 0, detail["total"])
            if data["status"] == "Extracting":
                self._download.done(layer_id)
                self._extract.update(layer_id, detail["current"], detail["total"])
            if data["status"] == "Pull complete":
                self._download.done(layer_id)
                self._extract.done(layer_id)
        except KeyError:
            pass

    def status(self):
        return {
            "name": self._interface.name,
            "downloading": {
                "current": self._download.current(),
                "total": self._download.total(),
            },
            "extracting": {
                "current": self._extract.current(),
                "total": self._extract.total(),
            },
        }
