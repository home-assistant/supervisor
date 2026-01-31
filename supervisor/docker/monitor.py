"""Supervisor docker monitor based on events."""

import asyncio
from dataclasses import dataclass
import logging
from typing import Any

import aiodocker

from ..const import BusEvent
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HassioError
from ..utils.sentry import capture_exception
from .const import LABEL_MANAGED, ContainerState

_LOGGER: logging.Logger = logging.getLogger(__name__)

STOP_MONITOR_TIMEOUT = 5.0


@dataclass(slots=True, frozen=True)
class DockerContainerStateEvent:
    """Event for docker container state change."""

    name: str
    state: ContainerState
    id: str
    time: int


@dataclass(slots=True, frozen=True)
class DockerEventCallbackTask:
    """Docker event and task spawned for it."""

    data: DockerContainerStateEvent
    task: asyncio.Task


class DockerMonitor(CoreSysAttributes):
    """Docker monitor for supervisor."""

    def __init__(self, coresys: CoreSys, docker_client: aiodocker.Docker):
        """Initialize Docker monitor object."""
        super().__init__()
        self.coresys = coresys
        self.docker = docker_client
        self._unlabeled_managed_containers: list[str] = []
        self._monitor_task: asyncio.Task | None = None
        self._await_task: asyncio.Task | None = None
        self._event_tasks: asyncio.Queue[DockerEventCallbackTask | None] = (
            asyncio.Queue()
        )

    def watch_container(self, container_metadata: dict[str, Any]):
        """If container is missing the managed label, add name to list."""
        labels: dict[str, str] = container_metadata.get("Config", {}).get("Labels", {})
        name: str | None = container_metadata.get("Name")
        if name:
            name = name.lstrip("/")

        if LABEL_MANAGED not in labels and name:
            self._unlabeled_managed_containers += [name]

    async def load(self):
        """Start docker events monitor."""
        self._monitor_task = self.sys_create_task(self._subscribe(), eager_start=True)
        self._await_task = self.sys_create_task(
            self._await_event_tasks(), eager_start=True
        )
        _LOGGER.info("Started docker events monitor")

    async def unload(self):
        """Stop docker events monitor."""
        await self.docker.events.stop()
        if self._monitor_task and self._await_task:
            await asyncio.wait(
                [self._monitor_task, self._await_task], timeout=STOP_MONITOR_TIMEOUT
            )
            self._monitor_task = None
            self._await_task = None
        _LOGGER.info("Stopped docker events monitor")

    async def _subscribe(self) -> None:
        """Monitor and process docker events."""
        events = self.docker.events.subscribe()

        while True:
            event: dict[str, Any] | None = await events.get()
            if event is None:
                break

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
                    state_event = DockerContainerStateEvent(
                        name=attributes["name"],
                        state=container_state,
                        id=event["Actor"]["ID"],
                        time=event["time"],
                    )
                    tasks = self.sys_bus.fire_event(
                        BusEvent.DOCKER_CONTAINER_STATE_CHANGE, state_event
                    )
                    await asyncio.gather(
                        *[
                            self._event_tasks.put(
                                DockerEventCallbackTask(state_event, task)
                            )
                            for task in tasks
                        ]
                    )

        await self._event_tasks.put(None)

    async def _await_event_tasks(self):
        """Await event callback tasks to clean up and capture output."""
        while (event := await self._event_tasks.get()) is not None:
            try:
                await event.task
            except HassioError:
                pass
            except Exception as err:  # pylint: disable=broad-exception-caught
                capture_exception(err)
                _LOGGER.error(
                    "Error encountered while processing docker container state event: %s %s %s",
                    event.task.get_name(),
                    event.data,
                    err,
                )
