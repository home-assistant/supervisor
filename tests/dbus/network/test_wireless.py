"""Test Network Manager Wireless object."""

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.network import NetworkManager
from supervisor.dbus.network.wireless import NetworkWireless

from tests.const import TEST_INTERFACE_WLAN_NAME
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.network_device_wireless import (
    DeviceWireless as DeviceWirelessService,
)


@pytest.fixture(name="device_wireless_service", autouse=True)
async def fixture_device_wireless_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> DeviceWirelessService:
    """Mock Device Wireless service."""
    yield network_manager_services["network_device_wireless"]


async def test_wireless(
    device_wireless_service: DeviceWirelessService, dbus_session_bus: MessageBus
):
    """Test wireless properties."""
    wireless = NetworkWireless("/org/freedesktop/NetworkManager/Devices/3")

    assert wireless.bitrate is None

    await wireless.connect(dbus_session_bus)

    assert wireless.bitrate == 0
    assert wireless.active is None

    device_wireless_service.emit_properties_changed(
        {"ActiveAccessPoint": "/org/freedesktop/NetworkManager/AccessPoint/43099"}
    )
    await device_wireless_service.ping()
    assert wireless.active is not None
    assert (
        wireless.active.object_path
        == "/org/freedesktop/NetworkManager/AccessPoint/43099"
    )

    device_wireless_service.emit_properties_changed({}, ["ActiveAccessPoint"])
    await device_wireless_service.ping()
    await device_wireless_service.ping()
    assert wireless.active is None


async def test_request_scan(
    network_manager: NetworkManager, device_wireless_service: DeviceWirelessService
):
    """Test request scan."""
    device_wireless_service.RequestScan.calls.clear()
    assert (
        await network_manager.get(TEST_INTERFACE_WLAN_NAME).wireless.request_scan()
        is None
    )
    assert device_wireless_service.RequestScan.calls == [({},)]


async def test_get_all_access_points(network_manager: NetworkManager):
    """Test get all access points."""
    accesspoints = await network_manager.get(
        TEST_INTERFACE_WLAN_NAME
    ).wireless.get_all_accesspoints()
    assert len(accesspoints) == 2
    assert accesspoints[0].mac == "E4:57:40:A9:D7:DE"
    assert accesspoints[0].mode == 2
    assert accesspoints[1].mac == "18:4B:0D:23:A1:9C"
    assert accesspoints[1].mode == 2


async def test_old_active_ap_disconnects(network_manager: NetworkManager):
    """Test old access point disconnects on active ap change."""
    wireless = network_manager.get(TEST_INTERFACE_WLAN_NAME).wireless

    await wireless.update(
        {"ActiveAccessPoint": "/org/freedesktop/NetworkManager/AccessPoint/43099"}
    )
    active = wireless.active
    assert active.is_connected is True

    await wireless.update({"ActiveAccessPoint": "/"})
    assert wireless.active is None
    assert active.is_connected is False
