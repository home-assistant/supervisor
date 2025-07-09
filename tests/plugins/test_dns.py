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


@pytest.fixture(name="mock_call_later")
def fixture_mock_call_later(coresys: CoreSys):
    """Mock sys_call_later with zero delay for testing."""

    def mock_call_later(_delay, *args, **kwargs) -> asyncio.TimerHandle:
        """Mock to remove delay."""
        return coresys.call_later(0, *args, **kwargs)

    return mock_call_later


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


async def test_notify_locals_changed_end_to_end_with_changes_and_running(
    coresys: CoreSys, mock_call_later
):
    """Test notify_locals_changed end-to-end: local DNS changes detected and plugin restarted."""
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
        patch.object(dns_plugin, "sys_call_later", new=mock_call_later),
    ):
        # Call notify_locals_changed
        dns_plugin.notify_locals_changed()

        # Wait for the async task to complete
        await asyncio.sleep(0.1)

        # Verify restart was called and cached locals were updated
        mock_restart.assert_called_once()
        assert dns_plugin._cached_locals == current_locals


async def test_notify_locals_changed_end_to_end_with_changes_but_not_running(
    coresys: CoreSys, mock_call_later
):
    """Test notify_locals_changed end-to-end: local DNS changes detected but plugin not running."""
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
        patch.object(dns_plugin, "sys_call_later", new=mock_call_later),
    ):
        # Call notify_locals_changed
        dns_plugin.notify_locals_changed()

        # Wait for the async task to complete
        await asyncio.sleep(0.1)

        # Verify restart was NOT called but cached locals were still updated
        mock_restart.assert_not_called()
        assert dns_plugin._cached_locals == current_locals


async def test_notify_locals_changed_end_to_end_no_changes(
    coresys: CoreSys, mock_call_later
):
    """Test notify_locals_changed end-to-end: no local DNS changes detected."""
    dns_plugin = coresys.plugins.dns

    # Set cached locals to match current network state
    current_locals = dns_plugin._compute_locals()
    dns_plugin._cached_locals = current_locals

    with (
        patch.object(dns_plugin, "restart") as mock_restart,
        patch.object(dns_plugin, "sys_call_later", new=mock_call_later),
    ):
        # Call notify_locals_changed
        dns_plugin.notify_locals_changed()

        # Wait for the async task to complete
        await asyncio.sleep(0.1)

        # Verify restart was NOT called since no changes
        mock_restart.assert_not_called()
        assert dns_plugin._cached_locals == current_locals


async def test_notify_locals_changed_debouncing_cancels_previous_timer(
    coresys: CoreSys,
):
    """Test notify_locals_changed debouncing cancels previous timer before creating new one."""
    dns_plugin = coresys.plugins.dns

    # Set cached locals to trigger change detection
    current_locals = dns_plugin._compute_locals()
    dns_plugin._cached_locals = (
        ["dns://192.168.1.1"]
        if current_locals != ["dns://192.168.1.1"]
        else ["dns://192.168.1.2"]
    )

    call_count = 0
    handles = []

    def mock_call_later_with_tracking(_delay, *args, **kwargs) -> asyncio.TimerHandle:
        """Mock to remove delay and track calls."""
        nonlocal call_count
        call_count += 1
        handle = coresys.call_later(0, *args, **kwargs)
        handles.append(handle)
        return handle

    with (
        patch.object(dns_plugin, "restart") as mock_restart,
        patch.object(dns_plugin.instance, "is_running", return_value=True),
        patch.object(dns_plugin, "sys_call_later", new=mock_call_later_with_tracking),
    ):
        # First call sets up timer
        dns_plugin.notify_locals_changed()
        assert call_count == 1
        first_handle = dns_plugin._locals_changed_handle
        assert first_handle is not None

        # Second call should cancel first timer and create new one
        dns_plugin.notify_locals_changed()
        assert call_count == 2
        second_handle = dns_plugin._locals_changed_handle
        assert second_handle is not None
        assert first_handle != second_handle

        # Wait for the async task to complete
        await asyncio.sleep(0.1)

        # Verify restart was called once for the final timer
        mock_restart.assert_called_once()
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


async def test_dns_restart_triggers_connectivity_check(coresys: CoreSys):
    """Test end-to-end that DNS container restart triggers connectivity check."""
    dns_plugin = coresys.plugins.dns

    # Load the plugin to register the event listener
    with (
        patch.object(type(dns_plugin.instance), "attach"),
        patch.object(type(dns_plugin.instance), "is_running", return_value=True),
    ):
        await dns_plugin.load()

    # Verify listener was registered (connectivity check listener should be stored)
    assert dns_plugin._connectivity_check_listener is not None

    # Create event to signal when connectivity check is called
    connectivity_check_event = asyncio.Event()

    # Mock connectivity check to set the event when called
    async def mock_check_connectivity():
        connectivity_check_event.set()

    with (
        patch.object(
            coresys.supervisor,
            "check_connectivity",
            side_effect=mock_check_connectivity,
        ),
        patch("supervisor.plugins.dns.asyncio.sleep") as mock_sleep,
    ):
        # Fire the DNS container state change event through bus system
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="hassio_dns",
                state=ContainerState.RUNNING,
                id="test_id",
                time=1234567890,
            ),
        )

        # Wait for connectivity check to be called
        await asyncio.wait_for(connectivity_check_event.wait(), timeout=1.0)

        # Verify sleep was called with correct delay
        mock_sleep.assert_called_once_with(5)

        # Reset and test that other containers don't trigger check
        connectivity_check_event.clear()
        mock_sleep.reset_mock()

        # Fire event for different container
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name="hassio_homeassistant",
                state=ContainerState.RUNNING,
                id="test_id",
                time=1234567890,
            ),
        )

        # Wait a bit and verify connectivity check was NOT triggered
        try:
            await asyncio.wait_for(connectivity_check_event.wait(), timeout=0.1)
            assert False, (
                "Connectivity check should not have been called for other containers"
            )
        except TimeoutError:
            # This is expected - connectivity check should not be called
            pass

        # Verify sleep was not called for other containers
        mock_sleep.assert_not_called()
