"""Test NetworkInterface."""

import logging
from unittest.mock import Mock, PropertyMock, patch

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.const import ConnectionStateType
from supervisor.dbus.network import NetworkManager
from supervisor.dbus.network.interface import NetworkInterface
from supervisor.exceptions import DBusFatalError, DBusParseError, HostNotSupportedError
from supervisor.utils.dbus import DBus

from tests.const import TEST_INTERFACE, TEST_INTERFACE_WLAN
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.network_connection_settings import SETTINGS_FIXTURE
from tests.dbus_service_mocks.network_manager import (
    NetworkManager as NetworkManagerService,
)


@pytest.fixture(name="network_manager_service", autouse=True)
async def fixture_network_manager_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> NetworkManagerService:
    """Mock NetworkManager dbus service."""
    yield network_manager_services["network_manager"]


async def test_network_manager(
    network_manager_service: NetworkManagerService, dbus_session_bus: MessageBus
):
    """Test network manager update."""
    network_manager = NetworkManager()

    assert network_manager.connectivity_enabled is None

    await network_manager.connect(dbus_session_bus)

    assert TEST_INTERFACE in network_manager
    assert network_manager.connectivity_enabled is True

    network_manager_service.emit_properties_changed({"ConnectivityCheckEnabled": False})
    await network_manager_service.ping()
    assert network_manager.connectivity_enabled is False

    network_manager_service.emit_properties_changed({}, ["ConnectivityCheckEnabled"])
    await network_manager_service.ping()
    await network_manager_service.ping()
    assert network_manager.connectivity_enabled is True


async def test_network_manager_version(
    network_manager_service: NetworkManagerService, network_manager: NetworkManager
):
    """Test if version validate work."""
    await network_manager._validate_version()
    assert network_manager.version == "1.22.10"

    network_manager_service.version = "1.13.9"
    with pytest.raises(HostNotSupportedError):
        await network_manager._validate_version()
    assert network_manager.version == "1.13.9"


async def test_check_connectivity(
    network_manager_service: NetworkManagerService, network_manager: NetworkManager
):
    """Test connectivity check."""
    network_manager_service.CheckConnectivity.calls.clear()

    assert await network_manager.check_connectivity() == 4
    assert network_manager_service.CheckConnectivity.calls == []

    assert await network_manager.check_connectivity(force=True) == 4
    assert network_manager_service.CheckConnectivity.calls == [tuple()]


async def test_activate_connection(
    network_manager_service: NetworkManagerService, network_manager: NetworkManager
):
    """Test activate connection."""
    network_manager_service.ActivateConnection.calls.clear()
    connection = await network_manager.activate_connection(
        "/org/freedesktop/NetworkManager/Settings/1",
        "/org/freedesktop/NetworkManager/Devices/1",
    )
    assert connection.state == ConnectionStateType.ACTIVATED
    assert (
        connection.settings.object_path == "/org/freedesktop/NetworkManager/Settings/1"
    )
    assert network_manager_service.ActivateConnection.calls == [
        (
            "/org/freedesktop/NetworkManager/Settings/1",
            "/org/freedesktop/NetworkManager/Devices/1",
            "/",
        )
    ]


async def test_add_and_activate_connection(
    network_manager_service: NetworkManagerService, network_manager: NetworkManager
):
    """Test add and activate connection."""
    network_manager_service.AddAndActivateConnection.calls.clear()

    settings, connection = await network_manager.add_and_activate_connection(
        SETTINGS_FIXTURE, "/org/freedesktop/NetworkManager/Devices/1"
    )
    assert settings.connection.uuid == "0c23631e-2118-355c-bbb0-8943229cb0d6"
    assert settings.ipv4.method == "auto"
    assert connection.state == ConnectionStateType.ACTIVATED
    assert (
        connection.settings.object_path == "/org/freedesktop/NetworkManager/Settings/1"
    )
    assert network_manager_service.AddAndActivateConnection.calls == [
        (SETTINGS_FIXTURE, "/org/freedesktop/NetworkManager/Devices/1", "/")
    ]


async def test_removed_devices_disconnect(
    network_manager_service: NetworkManagerService, network_manager: NetworkManager
):
    """Test removed devices are disconnected."""
    wlan = network_manager.get(TEST_INTERFACE_WLAN)
    assert wlan.is_connected is True

    network_manager_service.emit_properties_changed({"Devices": []})
    await network_manager_service.ping()

    assert TEST_INTERFACE_WLAN not in network_manager
    assert wlan.is_connected is False


async def test_handling_bad_devices(
    network_manager: NetworkManager,
    caplog: pytest.LogCaptureFixture,
    capture_exception: Mock,
):
    """Test handling of bad and disappearing devices."""
    caplog.clear()
    caplog.set_level(logging.INFO, "supervisor.dbus.network")

    with patch.object(DBus, "init_proxy", side_effect=DBusFatalError()):
        await network_manager.update(
            {"Devices": [device := "/org/freedesktop/NetworkManager/Devices/100"]}
        )
        assert f"Can't process {device}" not in caplog.text

    await network_manager.update()
    with patch.object(DBus, "properties", new=PropertyMock(return_value=None)):
        await network_manager.update(
            {"Devices": [device := "/org/freedesktop/NetworkManager/Devices/101"]}
        )
        assert f"Can't process {device}" not in caplog.text

    # Unparseable introspections shouldn't happen, this one is logged and captured
    await network_manager.update()
    with patch.object(DBus, "init_proxy", side_effect=(err := DBusParseError())):
        await network_manager.update(
            {"Devices": [device := "/org/freedesktop/NetworkManager/Devices/102"]}
        )
        assert f"Error while processing {device}" in caplog.text
        capture_exception.assert_called_once_with(err)

    # We should be able to debug these situations if necessary
    caplog.set_level(logging.DEBUG, "supervisor.dbus.network")
    await network_manager.update()
    with patch.object(DBus, "init_proxy", side_effect=DBusFatalError()):
        await network_manager.update(
            {"Devices": [device := "/org/freedesktop/NetworkManager/Devices/103"]}
        )
        assert f"Can't process {device}" in caplog.text

    await network_manager.update()
    with patch.object(DBus, "properties", new=PropertyMock(return_value=None)):
        await network_manager.update(
            {"Devices": [device := "/org/freedesktop/NetworkManager/Devices/104"]}
        )
        assert f"Can't process {device}" in caplog.text


async def test_ignore_veth_only_changes(
    network_manager_service: NetworkManagerService, network_manager: NetworkManager
):
    """Changes to list of devices is ignored unless it changes managed devices."""
    assert network_manager.properties["Devices"] == [
        "/org/freedesktop/NetworkManager/Devices/1",
        "/org/freedesktop/NetworkManager/Devices/3",
    ]
    with patch.object(NetworkInterface, "connect") as connect:
        network_manager_service.emit_properties_changed(
            {
                "Devices": [
                    "/org/freedesktop/NetworkManager/Devices/1",
                    "/org/freedesktop/NetworkManager/Devices/3",
                    "/org/freedesktop/NetworkManager/Devices/35",
                ]
            }
        )
        await network_manager_service.ping()
        connect.assert_not_called()

        network_manager_service.emit_properties_changed(
            {"Devices": ["/org/freedesktop/NetworkManager/Devices/35"]}
        )
        await network_manager_service.ping()
        connect.assert_called_once()
