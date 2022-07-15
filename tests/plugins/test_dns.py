"""Test DNS plugin."""
import asyncio
from ipaddress import IPv4Address
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from supervisor.const import BusEvent, LogLevel
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.interface import DockerInterface
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.plugins.dns import HostEntry
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

from tests.plugins.test_plugin_base import mock_current_state, mock_is_running


@pytest.fixture(name="docker_interface")
async def fixture_docker_interface() -> tuple[AsyncMock, AsyncMock]:
    """Mock docker interface methods."""
    with patch.object(DockerInterface, "run") as run, patch.object(
        DockerInterface, "restart"
    ) as restart:
        yield (run, restart)


@pytest.fixture(name="write_json")
async def fixture_write_json() -> Mock:
    """Mock json file writer."""
    with patch("supervisor.plugins.dns.write_json_file") as write_json_file:
        yield write_json_file


async def test_config_write(
    coresys: CoreSys,
    docker_interface: tuple[AsyncMock, AsyncMock],
    write_json: Mock,
):
    """Test config write on DNS start and restart."""
    assert coresys.plugins.dns.locals == ["dns://192.168.30.1"]
    coresys.plugins.dns.servers = ["dns://1.1.1.1", "dns://8.8.8.8"]

    await coresys.plugins.dns.start()
    docker_interface[0].assert_called_once()
    docker_interface[1].assert_not_called()

    write_json.assert_called_once_with(
        Path("/data/dns/coredns.json"),
        {
            "servers": ["dns://1.1.1.1", "dns://8.8.8.8"],
            "locals": ["dns://192.168.30.1"],
            "fallback": True,
            "debug": False,
        },
    )

    docker_interface[0].reset_mock()
    write_json.reset_mock()
    coresys.plugins.dns.servers = ["dns://8.8.8.8"]
    coresys.plugins.dns.fallback = False
    coresys.config.logging = LogLevel.DEBUG

    await coresys.plugins.dns.restart()
    docker_interface[0].assert_not_called()
    docker_interface[1].assert_called_once()

    write_json.assert_called_once_with(
        Path("/data/dns/coredns.json"),
        {
            "servers": ["dns://8.8.8.8"],
            "locals": ["dns://192.168.30.1"],
            "fallback": False,
            "debug": True,
        },
    )


async def test_reset(coresys: CoreSys):
    """Test reset returns dns plugin to defaults."""
    coresys.plugins.dns.servers = ["dns://1.1.1.1", "dns://8.8.8.8"]
    coresys.plugins.dns.fallback = False
    coresys.plugins.dns._loop = True  # pylint: disable=protected-access
    assert len(coresys.addons.installed) == 0

    with patch.object(
        type(coresys.plugins.dns.hosts), "unlink"
    ) as unlink, patch.object(type(coresys.plugins.dns), "write_hosts") as write_hosts:
        await coresys.plugins.dns.reset()

        assert coresys.plugins.dns.servers == []
        assert coresys.plugins.dns.fallback is True
        assert coresys.plugins.dns._loop is False  # pylint: disable=protected-access
        unlink.assert_called_once()
        write_hosts.assert_called_once()

        # pylint: disable=protected-access
        assert coresys.plugins.dns._hosts == [
            HostEntry(
                ip_address=IPv4Address("127.0.0.1"),
                names=["localhost", "localhost.local.hass.io"],
            ),
            HostEntry(
                ip_address=IPv4Address("172.30.32.2"),
                names=[
                    "hassio",
                    "hassio.local.hass.io",
                    "supervisor",
                    "supervisor.local.hass.io",
                ],
            ),
            HostEntry(
                ip_address=IPv4Address("172.30.32.1"),
                names=[
                    "homeassistant",
                    "homeassistant.local.hass.io",
                    "home-assistant",
                    "home-assistant.local.hass.io",
                ],
            ),
            HostEntry(
                ip_address=IPv4Address("172.30.32.3"),
                names=["dns", "dns.local.hass.io"],
            ),
            HostEntry(
                ip_address=IPv4Address("172.30.32.6"),
                names=["observer", "observer.local.hass.io"],
            ),
        ]


async def mock_logs(logs: bytes) -> bytes:
    """Mock for logs method."""
    return logs


async def test_loop_detection_on_failure(coresys: CoreSys):
    """Test loop detection when coredns fails."""
    assert len(coresys.resolution.issues) == 0
    assert len(coresys.resolution.suggestions) == 0

    with patch.object(type(coresys.plugins.dns.instance), "attach"), patch.object(
        type(coresys.plugins.dns.instance),
        "is_running",
        return_value=mock_is_running(True),
    ):
        await coresys.plugins.dns.load()

    with patch.object(type(coresys.plugins.dns), "rebuild") as rebuild, patch.object(
        type(coresys.plugins.dns.instance),
        "current_state",
        side_effect=[
            mock_current_state(ContainerState.FAILED),
            mock_current_state(ContainerState.FAILED),
        ],
    ), patch.object(type(coresys.plugins.dns.instance), "logs") as logs:
        logs.return_value = mock_logs(b"")
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="hassio_dns",
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        assert len(coresys.resolution.issues) == 0
        assert len(coresys.resolution.suggestions) == 0
        rebuild.assert_called_once()

        rebuild.reset_mock()
        logs.return_value = mock_logs(b"plugin/loop: Loop")
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="hassio_dns",
                state=ContainerState.FAILED,
                id="abc123",
                time=1,
            ),
        )
        await asyncio.sleep(0)
        assert coresys.resolution.issues == [
            Issue(IssueType.DNS_LOOP, ContextType.PLUGIN, "dns")
        ]
        assert coresys.resolution.suggestions == [
            Suggestion(SuggestionType.EXECUTE_RESET, ContextType.PLUGIN, "dns")
        ]
        rebuild.assert_called_once()
