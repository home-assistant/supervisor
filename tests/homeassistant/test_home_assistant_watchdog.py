"""Test Home Assistant watchdog."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

from awesomeversion import AwesomeVersion

from supervisor.const import BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import HomeAssistantError


async def test_home_assistant_watchdog(coresys: CoreSys) -> None:
    """Test homeassistant watchdog works correctly."""
    coresys.homeassistant.version = AwesomeVersion("2022.7.3")
    with (
        patch(
            "supervisor.docker.interface.DockerInterface.version",
            new=PropertyMock(return_value=AwesomeVersion("2022.7.3")),
        ),
        patch.object(type(coresys.homeassistant.core.instance), "attach"),
    ):
        await coresys.homeassistant.core.load()

    coresys.homeassistant.core.watchdog = True

    with (
        patch.object(type(coresys.homeassistant.core), "restart") as restart,
        patch.object(type(coresys.homeassistant.core), "start") as start,
        patch.object(
            type(coresys.homeassistant.core.instance), "current_state"
        ) as current_state,
    ):
        current_state.return_value = ContainerState.UNHEALTHY
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="homeassistant",
                state=ContainerState.UNHEALTHY,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        restart.assert_called_once()
        start.assert_not_called()

        restart.reset_mock()
        current_state.return_value = ContainerState.FAILED
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="homeassistant",
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        restart.assert_not_called()
        start.assert_called_once()

        start.reset_mock()
        # Do not process event if container state has changed since fired
        current_state.return_value = ContainerState.HEALTHY
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="homeassistant",
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        restart.assert_not_called()
        start.assert_not_called()

        # Do not restart when home assistant stopped normally
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="homeassistant",
                state=ContainerState.STOPPED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        restart.assert_not_called()
        start.assert_not_called()

        # Other containers ignored
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="addon_local_other",
                state=ContainerState.UNHEALTHY,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        restart.assert_not_called()
        start.assert_not_called()


async def test_home_assistant_watchdog_rebuild_on_failure(coresys: CoreSys) -> None:
    """Test home assistant watchdog rebuilds if start fails."""
    coresys.homeassistant.version = AwesomeVersion("2022.7.3")
    with (
        patch(
            "supervisor.docker.interface.DockerInterface.version",
            new=PropertyMock(return_value=AwesomeVersion("2022.7.3")),
        ),
        patch.object(type(coresys.homeassistant.core.instance), "attach"),
    ):
        await coresys.homeassistant.core.load()

    coresys.homeassistant.core.watchdog = True

    with (
        patch.object(
            type(coresys.homeassistant.core), "start", side_effect=HomeAssistantError()
        ) as start,
        patch.object(type(coresys.homeassistant.core), "rebuild") as rebuild,
        patch.object(
            type(coresys.homeassistant.core.instance),
            "current_state",
            return_value=ContainerState.FAILED,
        ),
    ):
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="homeassistant",
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0.1)
        start.assert_called_once()
        rebuild.assert_called_once()


async def test_home_assistant_watchdog_skip_on_load(
    coresys: CoreSys, container: MagicMock
) -> None:
    """Test home assistant watchdog skips a crash event on load."""
    container.status = "stopped"
    container.attrs["State"]["ExitCode"] = 1
    coresys.homeassistant.core.watchdog = True

    events = AsyncMock()
    coresys.bus.register_event(BusEvent.DOCKER_CONTAINER_STATE_CHANGE, events)

    coresys.homeassistant.version = AwesomeVersion("2022.7.3")
    with (
        patch(
            "supervisor.docker.interface.DockerInterface.version",
            new=PropertyMock(return_value=AwesomeVersion("2022.7.3")),
        ),
        patch.object(type(coresys.homeassistant.core), "restart") as restart,
        patch.object(type(coresys.homeassistant.core), "start") as start,
    ):
        await coresys.homeassistant.core.load()

        # No events should be raised on attach
        await asyncio.sleep(0)
        events.assert_not_called()
        restart.assert_not_called()
        start.assert_not_called()
