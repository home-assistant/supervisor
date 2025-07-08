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

        # Verify the hosts data structure is properly initialized
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


async def test_notify_locals_changed_always_schedules_debounce_timer(coresys: CoreSys):
    """Test notify_locals_changed always schedules a debounce timer regardless of changes."""
    dns_plugin = coresys.plugins.dns

    # Set initial cached locals to match current network state
    dns_plugin._cached_locals = dns_plugin._compute_locals()

    mock_handle = Mock()
    with patch.object(
        dns_plugin, "sys_call_later", return_value=mock_handle
    ) as mock_call_later:
        dns_plugin.notify_locals_changed()

        # Should always schedule restart timer - comparison happens in _restart_dns_after_locals_change
        mock_call_later.assert_called_once_with(
            1.0, dns_plugin._trigger_restart_dns_after_locals_change
        )
        assert dns_plugin._locals_changed_handle == mock_handle


async def test_notify_locals_changed_schedules_restart_timer(coresys: CoreSys):
    """Test notify_locals_changed schedules restart timer with correct parameters."""
    dns_plugin = coresys.plugins.dns

    # Set initial cached locals to something different from current state
    dns_plugin._cached_locals = ["dns://192.168.1.1"]

    mock_handle = Mock()
    with patch.object(
        dns_plugin, "sys_call_later", return_value=mock_handle
    ) as mock_call_later:
        dns_plugin.notify_locals_changed()

        # Should schedule restart with 1 second delay
        mock_call_later.assert_called_once_with(
            1.0, dns_plugin._trigger_restart_dns_after_locals_change
        )
        assert dns_plugin._locals_changed_handle == mock_handle


async def test_notify_locals_changed_schedules_timer_regardless_of_plugin_state(
    coresys: CoreSys,
):
    """Test notify_locals_changed schedules timer even if plugin is not running."""
    dns_plugin = coresys.plugins.dns

    # Set initial cached locals
    dns_plugin._cached_locals = ["dns://192.168.1.1"]

    mock_handle = Mock()
    with (
        patch.object(dns_plugin, "_compute_locals", return_value=["dns://192.168.1.2"]),
        patch.object(
            dns_plugin, "sys_call_later", return_value=mock_handle
        ) as mock_call_later,
    ):
        dns_plugin.notify_locals_changed()

        # Should still schedule restart timer even if not running
        # (the _restart_dns_after_locals_change method will check if running)
        mock_call_later.assert_called_once()
        assert dns_plugin._locals_changed_handle == mock_handle


async def test_notify_locals_changed_debouncing_cancels_previous_timer(
    coresys: CoreSys,
):
    """Test notify_locals_changed debouncing cancels previous timer before creating new one."""
    dns_plugin = coresys.plugins.dns

    # Set initial cached locals to trigger change detection
    dns_plugin._cached_locals = ["dns://192.168.1.1"]

    mock_handle1 = Mock()
    mock_handle2 = Mock()

    with patch.object(
        dns_plugin, "sys_call_later", side_effect=[mock_handle1, mock_handle2]
    ) as mock_call_later:
        # First call sets up timer
        dns_plugin.notify_locals_changed()
        assert dns_plugin._locals_changed_handle == mock_handle1
        assert mock_call_later.call_count == 1

        # Second call should cancel first timer and create new one
        dns_plugin.notify_locals_changed()
        mock_handle1.cancel.assert_called_once()
        assert dns_plugin._locals_changed_handle == mock_handle2
        assert mock_call_later.call_count == 2


async def test_restart_dns_after_locals_change_restarts_when_running(coresys: CoreSys):
    """Test _restart_dns_after_locals_change restarts DNS when plugin is running and locals changed."""
    dns_plugin = coresys.plugins.dns

    # Set cached locals to something different from current network state
    current_locals = dns_plugin._compute_locals()
    dns_plugin._cached_locals = (
        ["dns://192.168.1.1"]
        if current_locals != ["dns://192.168.1.1"]
        else ["dns://192.168.1.2"]
    )

    with (
        patch.object(dns_plugin, "restart") as mock_restart,
        patch.object(dns_plugin.instance, "is_running", return_value=True),
    ):
        await dns_plugin._restart_dns_after_locals_change()

        # Should restart when locals changed and plugin is running
        mock_restart.assert_called_once()
        # Cached locals should be updated to current network state
        assert dns_plugin._cached_locals == current_locals


async def test_restart_dns_after_locals_change_skips_restart_when_not_running(
    coresys: CoreSys,
):
    """Test _restart_dns_after_locals_change skips restart when plugin is not running."""
    dns_plugin = coresys.plugins.dns

    # Set cached locals to something different from current network state
    current_locals = dns_plugin._compute_locals()
    dns_plugin._cached_locals = (
        ["dns://192.168.1.1"]
        if current_locals != ["dns://192.168.1.1"]
        else ["dns://192.168.1.2"]
    )

    with (
        patch.object(dns_plugin, "restart") as mock_restart,
        patch.object(dns_plugin.instance, "is_running", return_value=False),
    ):
        await dns_plugin._restart_dns_after_locals_change()

        # Should not restart when plugin is not running
        mock_restart.assert_not_called()
        # Cached locals should still be updated to current network state
        assert dns_plugin._cached_locals == current_locals


async def test_restart_dns_after_locals_change_noop_when_no_change(coresys: CoreSys):
    """Test _restart_dns_after_locals_change is noop when locals haven't actually changed."""
    dns_plugin = coresys.plugins.dns

    # Set cached locals to match current network state
    current_locals = dns_plugin._compute_locals()
    dns_plugin._cached_locals = current_locals

    with patch.object(dns_plugin, "restart") as mock_restart:
        await dns_plugin._restart_dns_after_locals_change()

        # Should not restart when no change
        mock_restart.assert_not_called()
        # Cached locals should remain the same
        assert dns_plugin._cached_locals == current_locals


async def test_stop_cancels_pending_timers_and_tasks(coresys: CoreSys):
    """Test stop cancels pending locals change timers and restart tasks to prevent resource leaks."""
    dns_plugin = coresys.plugins.dns

    mock_timer_handle = Mock()
    mock_task_handle = Mock()
    dns_plugin._locals_changed_handle = mock_timer_handle
    dns_plugin._restart_after_locals_change_handle = mock_task_handle

    with patch.object(dns_plugin.instance, "stop"):
        await dns_plugin.stop()

    # Should cancel pending timer and task, then clean up
    mock_timer_handle.cancel.assert_called_once()
    mock_task_handle.cancel.assert_called_once()
    assert dns_plugin._locals_changed_handle is None
    assert dns_plugin._restart_after_locals_change_handle is None
