"""Supervisor docker monitor based on events."""

from contextlib import suppress
from dataclasses import dataclass
import logging
from threading import Thread

from docker.models.containers import Container
from docker.types.daemon import CancellableStream

from ..const import BusEvent
from ..coresys import CoreSys, CoreSysAttributes
from .const import LABEL_MANAGED, ContainerState

_LOGGER: logging.Logger = logging.getLogger(__name__)


@dataclass
class DockerContainerStateEvent:
    """Event for docker container state change."""

    name: str
    state: ContainerState
    id: str
    time: int


class DockerMonitor(CoreSysAttributes, Thread):
    """Docker monitor for supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker monitor object."""
        super().__init__()
        self.coresys = coresys
        self._events: CancellableStream | None = None
        self._unlabeled_managed_containers: list[str] = []

    def watch_container(self, container: Container):
        """If container is missing the managed label, add name to list."""
        if LABEL_MANAGED not in container.labels and container.name:
            self._unlabeled_managed_containers += [container.name]

    async def load(self):
        """Start docker events monitor."""
        self._events = self.sys_docker.events
        Thread.start(self)
        _LOGGER.info("Started docker events monitor")

    async def unload(self):
        """Stop docker events monitor."""
        self._events.close()
        with suppress(RuntimeError):
            self.join(timeout=5)

        _LOGGER.info("Stopped docker events monitor")

    def run(self) -> None:
        """Monitor and process docker events."""
        if not self._events:
            raise RuntimeError("Monitor has not been loaded!")

        for event in self._events:
            attributes: dict[str, str] = event.get("Actor", {}).get("Attributes", {})

            if event["Type"] == "container" and (
                LABEL_MANAGED in attributes
                or attributes.get("name") in self._unlabeled_managed_containers
            ):
                container_state: ContainerState | None = None
                action: str = event["Action"]

                if action == "start":
                    container_state = ContainerState.RUNNING
                elif action == "die":
                    container_state = (
                        ContainerState.STOPPED
                        if int(event["Actor"]["Attributes"]["exitCode"]) == 0
                        else ContainerState.FAILED
                    )
                elif action == "health_status: healthy":
                    container_state = ContainerState.HEALTHY
                elif action == "health_status: unhealthy":
                    container_state = ContainerState.UNHEALTHY

                if container_state:
                    self.sys_loop.call_soon_threadsafe(
                        self.sys_bus.fire_event,
                        BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
                        DockerContainerStateEvent(
                            name=attributes["name"],
                            state=container_state,
                            id=event["id"],
                            time=event["time"],
                        ),
                    )
