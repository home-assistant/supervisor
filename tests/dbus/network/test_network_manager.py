"""Test NetworkInterface."""
import asyncio
import logging
from unittest.mock import AsyncMock, PropertyMock, patch

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.const import ConnectionStateType
from supervisor.dbus.network import NetworkManager
from supervisor.dbus.network.interface import NetworkInterface
from supervisor.exceptions import DBusFatalError, DBusParseError, HostNotSupportedError
from supervisor.utils.dbus import DBus

from .setting.test_init import SETTINGS_WITH_SIGNATURE

from tests.common import fire_property_change_signal
from tests.const import TEST_INTERFACE, TEST_INTERFACE_WLAN

# pylint: disable=protected-access


@pytest.mark.asyncio
async def test_network_manager(network_manager: NetworkManager):
    """Test network manager update."""
    assert TEST_INTERFACE in network_manager.interfaces
    assert network_manager.connectivity_enabled is True

    fire_property_change_signal(network_manager, {"ConnectivityCheckEnabled": False})
    await asyncio.sleep(0)
    assert network_manager.connectivity_enabled is False

    fire_property_change_signal(network_manager, {"ConnectivityCheckEnabled": True})
    await asyncio.sleep(0)
    assert network_manager.connectivity_enabled is True


@pytest.mark.asyncio
async def test_network_manager_version(network_manager: NetworkManager):
    """Test if version validate work."""
    await network_manager._validate_version()
    assert network_manager.version == "1.22.10"

    network_manager.dbus.get_properties = AsyncMock(return_value={"Version": "1.13.9"})
    with pytest.raises(HostNotSupportedError):
        await network_manager._validate_version()
    assert network_manager.version == "1.13.9"


async def test_check_connectivity(network_manager: NetworkManager, dbus: list[str]):
    """Test connectivity check."""
    dbus.clear()
    assert await network_manager.check_connectivity() == 4
    assert dbus == [
        "/org/freedesktop/NetworkManager-org.freedesktop.NetworkManager.Connectivity"
    ]

    dbus.clear()
    assert await network_manager.check_connectivity(force=True) == 4
    assert dbus == [
        "/org/freedesktop/NetworkManager-org.freedesktop.NetworkManager.CheckConnectivity"
    ]


async def test_activate_connection(network_manager: NetworkManager, dbus: list[str]):
    """Test activate connection."""
    dbus.clear()
    connection = await network_manager.activate_connection(
        "/org/freedesktop/NetworkManager/Settings/1",
        "/org/freedesktop/NetworkManager/Devices/1",
    )
    assert connection.state == ConnectionStateType.ACTIVATED
    assert (
        connection.settings.object_path == "/org/freedesktop/NetworkManager/Settings/1"
    )
    assert dbus == [
        "/org/freedesktop/NetworkManager-org.freedesktop.NetworkManager.ActivateConnection",
        "/org/freedesktop/NetworkManager/Settings/1-org.freedesktop.NetworkManager.Settings.Connection.GetSettings",
    ]


async def test_add_and_activate_connection(
    network_manager: NetworkManager, dbus: list[str]
):
    """Test add and activate connection."""
    dbus.clear()
    settings, connection = await network_manager.add_and_activate_connection(
        SETTINGS_WITH_SIGNATURE, "/org/freedesktop/NetworkManager/Devices/1"
    )
    assert settings.connection.uuid == "0c23631e-2118-355c-bbb0-8943229cb0d6"
    assert settings.ipv4.method == "auto"
    assert connection.state == ConnectionStateType.ACTIVATED
    assert (
        connection.settings.object_path == "/org/freedesktop/NetworkManager/Settings/1"
    )
    assert dbus == [
        "/org/freedesktop/NetworkManager-org.freedesktop.NetworkManager.AddAndActivateConnection",
        "/org/freedesktop/NetworkManager/Settings/1-org.freedesktop.NetworkManager.Settings.Connection.GetSettings",
    ]


async def test_removed_devices_disconnect(network_manager: NetworkManager):
    """Test removed devices are disconnected."""
    wlan = network_manager.interfaces[TEST_INTERFACE_WLAN]
    assert wlan.is_connected is True

    fire_property_change_signal(
        network_manager, {"Devices": ["/org/freedesktop/NetworkManager/Devices/1"]}
    )
    await asyncio.sleep(0)

    assert TEST_INTERFACE_WLAN not in network_manager.interfaces
    assert wlan.is_connected is False


async def test_handling_bad_devices(
    network_manager: NetworkManager, caplog: pytest.LogCaptureFixture
):
    """Test handling of bad and disappearing devices."""
    caplog.clear()
    caplog.set_level(logging.INFO, "supervisor.dbus.network")

    with patch.object(DBus, "_init_proxy", side_effect=DBusFatalError()):
        await network_manager.update(
            {"Devices": ["/org/freedesktop/NetworkManager/Devices/100"]}
        )
        assert not caplog.text

    await network_manager.update()
    with patch.object(DBus, "properties", new=PropertyMock(return_value=None)):
        await network_manager.update(
            {"Devices": ["/org/freedesktop/NetworkManager/Devices/101"]}
        )
        assert not caplog.text

    # Unparseable introspections shouldn't happen, this one is logged and captured
    await network_manager.update()
    with patch.object(
        DBus, "_init_proxy", side_effect=(err := DBusParseError())
    ), patch("supervisor.dbus.network.sentry_sdk.capture_exception") as capture:
        await network_manager.update(
            {"Devices": [device := "/org/freedesktop/NetworkManager/Devices/102"]}
        )
        assert f"Error while processing {device}" in caplog.text
        capture.assert_called_once_with(err)

    # We should be able to debug these situations if necessary
    caplog.set_level(logging.DEBUG, "supervisor.dbus.network")
    await network_manager.update()
    with patch.object(DBus, "_init_proxy", side_effect=DBusFatalError()):
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
    network_manager: NetworkManager, dbus_bus: MessageBus
):
    """Changes to list of devices is ignored unless it changes managed devices."""
    assert network_manager.properties["Devices"] == [
        "/org/freedesktop/NetworkManager/Devices/1",
        "/org/freedesktop/NetworkManager/Devices/3",
    ]
    with patch.object(NetworkInterface, "update") as update:
        await network_manager.update(
            {
                "Devices": [
                    "/org/freedesktop/NetworkManager/Devices/1",
                    "/org/freedesktop/NetworkManager/Devices/3",
                    "/org/freedesktop/NetworkManager/Devices/35",
                ]
            }
        )
        update.assert_not_called()

        await network_manager.update(
            {"Devices": ["/org/freedesktop/NetworkManager/Devices/35"]}
        )
        update.assert_called_once()
