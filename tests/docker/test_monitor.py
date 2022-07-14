"""Test docker events monitor."""

import asyncio
from typing import Any, Optional
from unittest.mock import PropertyMock, patch

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
    coresys: CoreSys, event: dict[str, Any], expected: Optional[ContainerState]
):
    """Test events created from docker events."""
    event["Actor"]["Attributes"]["name"] = "some_container"
    event["id"] = "abc123"
    event["time"] = 123
    with patch(
        "supervisor.docker.manager.DockerAPI.events",
        new=PropertyMock(return_value=[event]),
    ), patch.object(type(coresys.bus), "fire_event") as fire_event:
        await coresys.docker.monitor.start()
        await asyncio.sleep(0)
        if expected:
            fire_event.assert_called_once_with(
                BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
                DockerContainerStateEvent("some_container", expected, "abc123", 123),
            )
        else:
            fire_event.assert_not_called()
