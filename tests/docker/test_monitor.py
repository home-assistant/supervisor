"""Test docker events monitor."""

import asyncio
from typing import Any
from unittest.mock import PropertyMock, patch

from aiodocker.containers import DockerContainer
from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.monitor import DockerContainerStateEvent


@pytest.mark.parametrize(
    "event,expected",
    [
        (
            {
                "Type": "container",
                "Action": "start",
                "Actor": {"Attributes": {"supervisor_managed": ""}},
            },
            ContainerState.RUNNING,
        ),
        (
            {
                "Type": "container",
                "Action": "die",
                "Actor": {"Attributes": {"supervisor_managed": "", "exitCode": "0"}},
            },
            ContainerState.STOPPED,
        ),
        (
            {
                "Type": "container",
                "Action": "die",
                "Actor": {"Attributes": {"supervisor_managed": "", "exitCode": "137"}},
            },
            ContainerState.FAILED,
        ),
        (
            {
                "Type": "container",
                "Action": "health_status: healthy",
                "Actor": {"Attributes": {"supervisor_managed": ""}},
            },
            ContainerState.HEALTHY,
        ),
        (
            {
                "Type": "container",
                "Action": "health_status: unhealthy",
                "Actor": {"Attributes": {"supervisor_managed": ""}},
            },
            ContainerState.UNHEALTHY,
        ),
        (
            {
                "Type": "container",
                "Action": "exec_die",
                "Actor": {"Attributes": {"supervisor_managed": ""}},
            },
            None,
        ),
        (
            {
                "Type": "container",
                "Action": "start",
                "Actor": {"Attributes": {}},
            },
            None,
        ),
        (
            {
                "Type": "network",
                "Action": "start",
                "Actor": {"Attributes": {}},
            },
            None,
        ),
    ],
)
async def test_events(
    coresys: CoreSys, event: dict[str, Any], expected: ContainerState | None
):
    """Test events created from docker events."""
    event["Actor"]["Attributes"]["name"] = "some_container"
    event["Actor"]["ID"] = "abc123"
    event["time"] = 123
    with (
        patch(
            "supervisor.docker.manager.DockerAPI.events",
            new=PropertyMock(return_value=[event]),
        ),
        patch.object(type(coresys.bus), "fire_event") as fire_event,
    ):
        await coresys.docker.monitor.load()
        await asyncio.sleep(0.1)
        if expected:
            fire_event.assert_called_once_with(
                BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
                DockerContainerStateEvent("some_container", expected, "abc123", 123),
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

    with (
        patch(
            "supervisor.docker.manager.DockerAPI.events",
            new=PropertyMock(
                return_value=[
                    {
                        "time": 123,
                        "Type": "container",
                        "Action": "die",
                        "Actor": {
                            "ID": "abc123",
                            "Attributes": {"name": "homeassistant", "exitCode": "137"},
                        },
                    }
                ]
            ),
        ),
        patch.object(type(coresys.bus), "fire_event") as fire_event,
    ):
        await coresys.docker.monitor.load()
        await asyncio.sleep(0.1)
        fire_event.assert_called_once_with(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                "homeassistant", ContainerState.FAILED, "abc123", 123
            ),
        )
