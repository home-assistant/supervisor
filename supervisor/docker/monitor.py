"""Supervisor docker monitor based on events."""
from dataclasses import dataclass
import logging
from typing import Optional

from docker.types.daemon import CancellableStream

from supervisor.const import BusEvent
from supervisor.coresys import CoreSys, CoreSysAttributes

from .const import LABEL_MANAGED, ContainerState

_LOGGER: logging.Logger = logging.getLogger(__name__)


@dataclass
class DockerContainerStateEvent:
    """Event for docker container state change."""

    name: str
    state: ContainerState
    id: str
    time: int


class DockerMonitor(CoreSysAttributes):
    """Docker monitor for supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker monitor object."""
        self.coresys = coresys
        self._events: Optional[CancellableStream] = None

    async def load(self):
        """Start docker events monitor."""
        self._events = self.sys_docker.events
        self.sys_create_task(self._monitor())
        _LOGGER.info("Started docker events monitor")

    async def unload(self):
        """Stop docker events monitor."""
        self._events.close()
        _LOGGER.info("Stopped docker events monitor")

    async def _monitor(self):
        """Monitor and process docker events."""
        for event in self._events:
            attributes: dict[str, str] = event.get("Actor", {}).get("Attributes", {})

            if event["Type"] == "container" and LABEL_MANAGED in attributes:
                container_state: Optional[ContainerState] = None
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
                    self.sys_bus.fire_event(
                        BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
                        DockerContainerStateEvent(
                            name=attributes["name"],
                            state=container_state,
                            id=event["id"],
                            time=event["time"],
                        ),
                    )
