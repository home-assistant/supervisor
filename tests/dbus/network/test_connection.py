"""Test connection object."""

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.const import ConnectionStateFlags
from supervisor.dbus.network import NetworkManager
from supervisor.dbus.network.connection import NetworkConnection

from tests.const import TEST_INTERFACE_ETH_NAME
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.network_active_connection import (
    ActiveConnection as ActiveConnectionService,
)


@pytest.fixture(name="active_connection_service", autouse=True)
async def fixture_active_connection_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> ActiveConnectionService:
    """Mock Active Connection service."""
    yield network_manager_services["network_active_connection"]


async def test_active_connection(
    active_connection_service: ActiveConnectionService, dbus_session_bus: MessageBus
):
    """Test active connection."""
    active_connection = NetworkConnection(
        "/org/freedesktop/NetworkManager/ActiveConnection/1"
    )

    assert active_connection.id is None

    await active_connection.connect(dbus_session_bus)

    assert active_connection.id == "Wired connection 1"
    assert active_connection.uuid == "0c23631e-2118-355c-bbb0-8943229cb0d6"
    assert active_connection.state_flags == {
        ConnectionStateFlags.LIFETIME_BOUND_TO_PROFILE_VISIBILITY,
        ConnectionStateFlags.IP6_READY,
        ConnectionStateFlags.IP4_READY,
        ConnectionStateFlags.LAYER2_READY,
    }

    active_connection_service.emit_properties_changed({"Id": "Wired connection 2"})
    await active_connection_service.ping()
    assert active_connection.id == "Wired connection 2"

    active_connection_service.emit_properties_changed({}, ["Id"])
    await active_connection_service.ping()
    await active_connection_service.ping()
    assert active_connection.id == "Wired connection 1"


async def test_old_ipv4_disconnect(
    network_manager: NetworkManager, active_connection_service: ActiveConnectionService
):
    """Test old ipv4 disconnects on ipv4 change."""
    connection = network_manager.get(TEST_INTERFACE_ETH_NAME).connection
    ipv4 = connection.ipv4
    assert ipv4.is_connected is True

    active_connection_service.emit_properties_changed({"Ip4Config": "/"})
    await active_connection_service.ping()

    assert connection.ipv4 is None
    assert ipv4.is_connected is False


async def test_old_ipv6_disconnect(
    network_manager: NetworkManager, active_connection_service: ActiveConnectionService
):
    """Test old ipv6 disconnects on ipv6 change."""
    connection = network_manager.get(TEST_INTERFACE_ETH_NAME).connection
    ipv6 = connection.ipv6
    assert ipv6.is_connected is True

    active_connection_service.emit_properties_changed({"Ip6Config": "/"})
    await active_connection_service.ping()

    assert connection.ipv6 is None
    assert ipv6.is_connected is False


async def test_old_settings_disconnect(
    network_manager: NetworkManager, active_connection_service: ActiveConnectionService
):
    """Test old settings disconnects on settings change."""
    connection = network_manager.get(TEST_INTERFACE_ETH_NAME).connection
    settings = connection.settings
    assert settings.is_connected is True

    active_connection_service.emit_properties_changed({"Connection": "/"})
    await active_connection_service.ping()

    assert connection.settings is None
    assert settings.is_connected is False
