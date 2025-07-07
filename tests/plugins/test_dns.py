"""Test DNS plugin."""

import asyncio
import errno
from ipaddress import IPv4Address
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from supervisor.const import BusEvent, LogLevel
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.dns import DockerDNS
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.plugins.dns import HostEntry
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion


@pytest.fixture(name="docker_interface")
async def fixture_docker_interface() -> tuple[AsyncMock, AsyncMock]:
    """Mock docker interface methods."""
    with (
        patch.object(DockerDNS, "run") as run,
        patch.object(DockerDNS, "restart") as restart,
    ):
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

    with (
        patch.object(type(coresys.plugins.dns.hosts), "unlink") as unlink,
        patch.object(type(coresys.plugins.dns), "write_hosts") as write_hosts,
    ):
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


async def test_loop_detection_on_failure(coresys: CoreSys):
    """Test loop detection when coredns fails."""
    assert len(coresys.resolution.issues) == 0
    assert len(coresys.resolution.suggestions) == 0

    with (
        patch.object(type(coresys.plugins.dns.instance), "attach"),
        patch.object(
            type(coresys.plugins.dns.instance),
            "is_running",
            return_value=True,
        ),
    ):
        await coresys.plugins.dns.load()

    with (
        patch.object(type(coresys.plugins.dns), "rebuild") as rebuild,
        patch.object(
            type(coresys.plugins.dns.instance),
            "current_state",
            side_effect=[
                ContainerState.FAILED,
                ContainerState.FAILED,
            ],
        ),
        patch.object(type(coresys.plugins.dns.instance), "logs") as logs,
    ):
        logs.return_value = b""
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
        logs.return_value = b"plugin/loop: Loop"
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


async def test_load_error(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture, container
):
    """Test error reading config files during load."""
    with (
        patch("supervisor.plugins.dns.Path.read_text", side_effect=(err := OSError())),
        patch("supervisor.plugins.dns.Path.write_text", side_effect=err),
    ):
        err.errno = errno.EBUSY
        await coresys.plugins.dns.load()

        assert "Can't read resolve.tmpl" in caplog.text
        assert "Can't read hosts.tmpl" in caplog.text
        assert coresys.core.healthy is True

        caplog.clear()
        err.errno = errno.EBADMSG
        await coresys.plugins.dns.load()

        assert "Can't read resolve.tmpl" in caplog.text
        assert "Can't read hosts.tmpl" in caplog.text
        assert coresys.core.healthy is False


async def test_load_error_writing_resolv(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture, container
):
    """Test error writing resolv during load."""
    with patch(
        "supervisor.plugins.dns.Path.write_text", side_effect=(err := OSError())
    ):
        err.errno = errno.EBUSY
        await coresys.plugins.dns.load()

        assert "Can't write/update /etc/resolv.conf" in caplog.text
        assert coresys.core.healthy is True

        caplog.clear()
        err.errno = errno.EBADMSG
        await coresys.plugins.dns.load()

        assert "Can't write/update /etc/resolv.conf" in caplog.text
        assert coresys.core.healthy is False


async def test_notify_locals_changed_no_change(coresys: CoreSys):
    """Test notify_locals_changed when DNS locals haven't changed."""
    dns_plugin = coresys.plugins.dns

    # Set initial cached locals
    dns_plugin._cached_locals = ["dns://192.168.1.1"]

    with (
        patch.object(dns_plugin, "_compute_locals", return_value=["dns://192.168.1.1"]),
        patch.object(dns_plugin, "restart") as mock_restart,
        patch.object(dns_plugin.instance, "is_running", return_value=True),
    ):
        await dns_plugin.notify_locals_changed()

        # Should not restart when locals haven't changed
        mock_restart.assert_not_called()
        # Cached locals should remain the same
        assert dns_plugin._cached_locals == ["dns://192.168.1.1"]


async def test_notify_locals_changed_with_changes_plugin_running(coresys: CoreSys):
    """Test notify_locals_changed when DNS locals changed and plugin is running."""
    dns_plugin = coresys.plugins.dns

    # Set initial cached locals
    dns_plugin._cached_locals = ["dns://192.168.1.1"]

    with (
        patch.object(dns_plugin, "_compute_locals", return_value=["dns://192.168.1.2"]),
        patch.object(dns_plugin, "restart") as mock_restart,
        patch.object(dns_plugin.instance, "is_running", return_value=True),
        patch.object(
            coresys.supervisor, "check_connectivity_unthrottled"
        ) as mock_connectivity,
        patch("asyncio.sleep") as mock_sleep,
    ):
        await dns_plugin.notify_locals_changed()

        # Should restart when locals changed and plugin is running
        mock_restart.assert_called_once()
        # Should sleep for 5 seconds
        mock_sleep.assert_called_once_with(5)
        # Should check connectivity
        mock_connectivity.assert_called_once()
        # Cached locals should be updated
        assert dns_plugin._cached_locals == ["dns://192.168.1.2"]


async def test_notify_locals_changed_with_changes_plugin_not_running(coresys: CoreSys):
    """Test notify_locals_changed when DNS locals changed but plugin is not running."""
    dns_plugin = coresys.plugins.dns

    # Set initial cached locals
    dns_plugin._cached_locals = ["dns://192.168.1.1"]

    with (
        patch.object(dns_plugin, "_compute_locals", return_value=["dns://192.168.1.2"]),
        patch.object(dns_plugin, "restart") as mock_restart,
        patch.object(dns_plugin.instance, "is_running", return_value=False),
        patch.object(
            coresys.supervisor, "check_connectivity_unthrottled"
        ) as mock_connectivity,
        patch("asyncio.sleep") as mock_sleep,
    ):
        await dns_plugin.notify_locals_changed()

        # Should not restart when plugin is not running
        mock_restart.assert_not_called()
        # Should not sleep or check connectivity
        mock_sleep.assert_not_called()
        mock_connectivity.assert_not_called()
        # Cached locals should still be updated
        assert dns_plugin._cached_locals == ["dns://192.168.1.2"]


async def test_notify_locals_changed_cached_locals_none(coresys: CoreSys):
    """Test notify_locals_changed when cached locals is None (first run)."""
    dns_plugin = coresys.plugins.dns

    # Set cached locals to None (initial state)
    dns_plugin._cached_locals = None

    with (
        patch.object(dns_plugin, "_compute_locals", return_value=["dns://192.168.1.1"]),
        patch.object(dns_plugin, "restart") as mock_restart,
        patch.object(dns_plugin.instance, "is_running", return_value=True),
        patch.object(
            coresys.supervisor, "check_connectivity_unthrottled"
        ) as mock_connectivity,
        patch("asyncio.sleep") as mock_sleep,
    ):
        await dns_plugin.notify_locals_changed()

        # Should restart when cached locals is None and new locals exist
        mock_restart.assert_called_once()
        # Should sleep and check connectivity
        mock_sleep.assert_called_once_with(5)
        mock_connectivity.assert_called_once()
        # Cached locals should be set
        assert dns_plugin._cached_locals == ["dns://192.168.1.1"]


async def test_notify_locals_changed_empty_to_populated(coresys: CoreSys):
    """Test notify_locals_changed when going from empty to populated locals."""
    dns_plugin = coresys.plugins.dns

    # Set initial cached locals to empty
    dns_plugin._cached_locals = []

    with (
        patch.object(dns_plugin, "_compute_locals", return_value=["dns://192.168.1.1"]),
        patch.object(dns_plugin, "restart") as mock_restart,
        patch.object(dns_plugin.instance, "is_running", return_value=True),
        patch.object(
            coresys.supervisor, "check_connectivity_unthrottled"
        ) as mock_connectivity,
        patch("asyncio.sleep") as mock_sleep,
    ):
        await dns_plugin.notify_locals_changed()

        # Should restart when going from empty to populated
        mock_restart.assert_called_once()
        mock_sleep.assert_called_once_with(5)
        mock_connectivity.assert_called_once()
        assert dns_plugin._cached_locals == ["dns://192.168.1.1"]


async def test_notify_locals_changed_populated_to_empty(coresys: CoreSys):
    """Test notify_locals_changed when going from populated to empty locals."""
    dns_plugin = coresys.plugins.dns

    # Set initial cached locals
    dns_plugin._cached_locals = ["dns://192.168.1.1"]

    with (
        patch.object(dns_plugin, "_compute_locals", return_value=[]),
        patch.object(dns_plugin, "restart") as mock_restart,
        patch.object(dns_plugin.instance, "is_running", return_value=True),
        patch.object(
            coresys.supervisor, "check_connectivity_unthrottled"
        ) as mock_connectivity,
        patch("asyncio.sleep") as mock_sleep,
    ):
        await dns_plugin.notify_locals_changed()

        # Should restart when going from populated to empty
        mock_restart.assert_called_once()
        mock_sleep.assert_called_once_with(5)
        mock_connectivity.assert_called_once()
        assert dns_plugin._cached_locals == []


async def test_notify_locals_changed_multiple_servers_change(coresys: CoreSys):
    """Test notify_locals_changed with multiple DNS servers changing."""
    dns_plugin = coresys.plugins.dns

    # Set initial cached locals with multiple servers
    dns_plugin._cached_locals = ["dns://192.168.1.1", "dns://192.168.1.2"]

    with (
        patch.object(
            dns_plugin,
            "_compute_locals",
            return_value=["dns://192.168.1.3", "dns://192.168.1.4"],
        ),
        patch.object(dns_plugin, "restart") as mock_restart,
        patch.object(dns_plugin.instance, "is_running", return_value=True),
        patch.object(
            coresys.supervisor, "check_connectivity_unthrottled"
        ) as mock_connectivity,
        patch("asyncio.sleep") as mock_sleep,
    ):
        await dns_plugin.notify_locals_changed()

        # Should restart when servers change
        mock_restart.assert_called_once()
        mock_sleep.assert_called_once_with(5)
        mock_connectivity.assert_called_once()
        assert dns_plugin._cached_locals == ["dns://192.168.1.3", "dns://192.168.1.4"]


async def test_notify_locals_no_change(coresys: CoreSys):
    """Test notify_locals_changed when DNS locals haven't changed."""
    dns_plugin = coresys.plugins.dns
    dns_plugin._cached_locals = ["dns://192.168.1.1"]

    with patch.object(
        dns_plugin, "_compute_locals", return_value=["dns://192.168.1.1"]
    ):
        await dns_plugin.notify_locals_changed()
        assert dns_plugin._cached_locals == ["dns://192.168.1.1"]


async def test_notify_locals_changed_plugin_running(coresys: CoreSys):
    """Test notify_locals_changed when DNS locals changed and plugin is running."""
    dns_plugin = coresys.plugins.dns
    dns_plugin._cached_locals = ["dns://192.168.1.1"]

    with (
        patch.object(dns_plugin, "_compute_locals", return_value=["dns://192.168.1.2"]),
        patch.object(dns_plugin, "restart") as mock_restart,
        patch.object(dns_plugin.instance, "is_running", return_value=True),
        patch.object(
            coresys.supervisor, "check_connectivity_unthrottled"
        ) as mock_connectivity,
        patch("asyncio.sleep") as mock_sleep,
    ):
        await dns_plugin.notify_locals_changed()

        mock_restart.assert_called_once()
        mock_sleep.assert_called_once_with(5)
        mock_connectivity.assert_called_once()
        assert dns_plugin._cached_locals == ["dns://192.168.1.2"]


async def test_notify_locals_changed_plugin_not_running(coresys: CoreSys):
    """Test notify_locals_changed when DNS locals changed but plugin is not running."""
    dns_plugin = coresys.plugins.dns
    dns_plugin._cached_locals = ["dns://192.168.1.1"]

    with (
        patch.object(dns_plugin, "_compute_locals", return_value=["dns://192.168.1.2"]),
        patch.object(dns_plugin, "restart") as mock_restart,
        patch.object(dns_plugin.instance, "is_running", return_value=False),
    ):
        await dns_plugin.notify_locals_changed()

        mock_restart.assert_not_called()
        assert dns_plugin._cached_locals == ["dns://192.168.1.2"]
