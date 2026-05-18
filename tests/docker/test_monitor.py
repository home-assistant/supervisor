"""Test docker events monitor."""

import asyncio
from typing import Any
from unittest.mock import patch

from aiodocker.containers import DockerContainer
from awesomeversion import AwesomeVersion
import pytest

from supervisor.bus import Bus
from supervisor.const import BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.monitor import DockerContainerStateEvent


@pytest.mark.parametrize(
    "event,expected,expected_exit_code",
    [
        (
            {
                "Type": "container",
                "Action": "start",
                "Actor": {"Attributes": {"supervisor_managed": ""}},
            },
            ContainerState.RUNNING,
            None,
        ),
        (
            {
                "Type": "container",
                "Action": "die",
                "Actor": {"Attributes": {"supervisor_managed": "", "exitCode": "0"}},
            },
            ContainerState.STOPPED,
            0,
        ),
        (
            {
                "Type": "container",
                "Action": "die",
                "Actor": {"Attributes": {"supervisor_managed": "", "exitCode": "137"}},
            },
            ContainerState.FAILED,
            137,
        ),
        (
            {
                "Type": "container",
                "Action": "health_status: healthy",
                "Actor": {"Attributes": {"supervisor_managed": ""}},
            },
            ContainerState.HEALTHY,
            None,
        ),
        (
            {
                "Type": "container",
                "Action": "health_status: unhealthy",
                "Actor": {"Attributes": {"supervisor_managed": ""}},
            },
            ContainerState.UNHEALTHY,
            None,
        ),
        (
            {
                "Type": "container",
                "Action": "exec_die",
                "Actor": {"Attributes": {"supervisor_managed": ""}},
            },
            None,
            None,
        ),
        (
            {
                "Type": "container",
                "Action": "start",
                "Actor": {"Attributes": {}},
            },
            None,
            None,
        ),
        (
            {
                "Type": "network",
                "Action": "start",
                "Actor": {"Attributes": {}},
            },
            None,
            None,
        ),
    ],
)
async def test_events(
    coresys: CoreSys,
    event: dict[str, Any],
    expected: ContainerState | None,
    expected_exit_code: int | None,
):
    """Test events created from docker events."""
    event["Actor"]["Attributes"]["name"] = "some_container"
    event["Actor"]["ID"] = "abc123"
    event["time"] = 123

    with patch.object(
        Bus, "fire_event", return_value=[coresys.create_task(asyncio.sleep(0))]
    ) as fire_event:
        await coresys.docker.docker.events.channel.publish(event)
        await asyncio.sleep(0)
        await coresys.docker.monitor.unload()
        if expected:
            fire_event.assert_called_once_with(
                BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
                DockerContainerStateEvent(
                    "some_container", expected, "abc123", 123, expected_exit_code
                ),
            )
        else:
            fire_event.assert_not_called()


async def test_unlabeled_container(coresys: CoreSys, container: DockerContainer):
    """Test attaching to unlabeled container is still watched."""
    container.id = "abc123"
    container.show.return_value = {
        "Name": "homeassistant",
        "Id": "abc123",
        "State": {"Status": "running"},
        "Config": {},
    }
    await coresys.homeassistant.core.instance.attach(AwesomeVersion("2022.7.3"))

    with patch.object(
        Bus, "fire_event", return_value=[coresys.create_task(asyncio.sleep(0))]
    ) as fire_event:
        await coresys.docker.docker.events.channel.publish(
            {
                "time": 123,
                "Type": "container",
                "Action": "die",
                "Actor": {
                    "ID": "abc123",
                    "Attributes": {"name": "homeassistant", "exitCode": "137"},
                },
            }
        )
        await coresys.docker.monitor.unload()
        fire_event.assert_called_once_with(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                "homeassistant", ContainerState.FAILED, "abc123", 123, 137
            ),
        )
