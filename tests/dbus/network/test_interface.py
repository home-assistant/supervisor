"""Test NetwrokInterface."""

from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.const import DeviceType, InterfaceMethod
from supervisor.dbus.network import NetworkManager
from supervisor.dbus.network.interface import NetworkInterface

from tests.common import mock_dbus_services
from tests.const import TEST_INTERFACE_ETH_NAME, TEST_INTERFACE_WLAN_NAME
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.network_device import Device as DeviceService


@pytest.fixture(name="device_eth0_service")
async def fixture_device_eth0_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> DeviceService:
    """Mock Device eth0 service."""
    yield network_manager_services["network_device"][
        "/org/freedesktop/NetworkManager/Devices/1"
    ]


@pytest.fixture(name="device_wlan0_service")
async def fixture_device_wlan0_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> DeviceService:
    """Mock Device wlan0 service."""
    yield network_manager_services["network_device"][
        "/org/freedesktop/NetworkManager/Devices/3"
    ]


@pytest.fixture(name="device_unmanaged_service")
async def fixture_device_unmanaged_service(
    dbus_session_bus: MessageBus,
) -> DeviceService:
    """Mock Device unmanaged service."""
    yield (
        await mock_dbus_services(
            {"network_device": "/org/freedesktop/NetworkManager/Devices/35"},
            dbus_session_bus,
        )
    )["network_device"]


async def test_network_interface_ethernet(
    device_eth0_service: DeviceService, dbus_session_bus: MessageBus
):
    """Test network interface."""
    interface = NetworkInterface("/org/freedesktop/NetworkManager/Devices/1")

    assert interface.sync_properties is False
    assert interface.name is None
    assert interface.type is None

    await interface.connect(dbus_session_bus)

    assert interface.sync_properties is True
    assert interface.name == TEST_INTERFACE_ETH_NAME
    assert interface.type == DeviceType.ETHERNET
    assert interface.managed is True
    assert interface.wireless is None
    assert interface.connection.state == 2
    assert interface.connection.uuid == "0c23631e-2118-355c-bbb0-8943229cb0d6"

    assert interface.connection.ipv4.address == [IPv4Interface("192.168.2.148/24")]
    assert interface.connection.ipv6.address == [
        IPv6Interface("2a03:169:3df5:0:6be9:2588:b26a:a679/64"),
        IPv6Interface("2a03:169:3df5::2f1/128"),
    ]

    assert interface.connection.ipv4.gateway == IPv4Address("192.168.2.1")
    assert interface.connection.ipv6.gateway == IPv6Address("fe80::da58:d7ff:fe00:9c69")

    assert interface.connection.ipv4.nameservers == [IPv4Address("192.168.2.2")]
    assert interface.connection.ipv6.nameservers == [
        IPv6Address("2001:1620:2777:1::10"),
        IPv6Address("2001:1620:2777:2::20"),
    ]

    assert interface.settings.ipv4.method == InterfaceMethod.AUTO
    assert interface.settings.ipv6.method == InterfaceMethod.AUTO
    assert interface.settings.connection.id == "Wired connection 1"

    device_eth0_service.emit_properties_changed({"Managed": False})
    await device_eth0_service.ping()
    assert interface.managed is False

    device_eth0_service.emit_properties_changed({}, ["Managed"])
    await device_eth0_service.ping()
    await device_eth0_service.ping()
    assert interface.managed is True


async def test_network_interface_wlan(
    device_wlan0_service: DeviceService, dbus_session_bus: MessageBus
):
    """Test wlan network interface."""
    interface = NetworkInterface("/org/freedesktop/NetworkManager/Devices/3")

    assert interface.wireless is None

    await interface.connect(dbus_session_bus)

    assert interface.sync_properties is True
    assert interface.name == TEST_INTERFACE_WLAN_NAME
    assert interface.type == DeviceType.WIRELESS
    assert interface.wireless is not None
    assert interface.wireless.bitrate == 0


async def test_old_connection_disconnect(
    network_manager: NetworkManager, device_eth0_service: DeviceService
):
    """Test old connection disconnects on connection change."""
    interface = network_manager.get(TEST_INTERFACE_ETH_NAME)
    connection = interface.connection
    assert connection.is_connected is True

    device_eth0_service.emit_properties_changed({"ActiveConnection": "/"})
    await device_eth0_service.ping()

    assert interface.connection is None
    assert connection.is_connected is False


async def test_old_wireless_disconnect(
    network_manager: NetworkManager, device_wlan0_service: DeviceService
):
    """Test old wireless disconnects on type change."""
    interface = network_manager.get(TEST_INTERFACE_WLAN_NAME)
    wireless = interface.wireless
    assert wireless.is_connected is True

    device_wlan0_service.emit_properties_changed({"DeviceType": DeviceType.ETHERNET})
    await device_wlan0_service.ping()

    assert interface.wireless is None
    assert wireless.is_connected is False


async def test_unmanaged_interface(
    device_unmanaged_service: DeviceService, dbus_session_bus: MessageBus
):
    """Test unmanaged interfaces don't sync properties."""
    interface = NetworkInterface("/org/freedesktop/NetworkManager/Devices/35")
    await interface.connect(dbus_session_bus)

    assert interface.managed is False
    assert interface.connection is None
    assert interface.driver == "veth"
    assert interface.sync_properties is False

    device_unmanaged_service.emit_properties_changed({"Driver": "test"})
    await device_unmanaged_service.ping()
    assert interface.driver == "veth"


async def test_interface_becomes_unmanaged(
    network_manager: NetworkManager,
    device_eth0_service: DeviceService,
    device_wlan0_service: DeviceService,
):
    """Test managed objects disconnect when interface becomes unmanaged."""
    eth0 = network_manager.get(TEST_INTERFACE_ETH_NAME)
    connection = eth0.connection
    wlan0 = network_manager.get(TEST_INTERFACE_WLAN_NAME)
    wireless = wlan0.wireless

    assert connection.is_connected is True
    assert wireless.is_connected is True

    device_eth0_service.emit_properties_changed({"Managed": False})
    await device_eth0_service.ping()
    device_wlan0_service.emit_properties_changed({"Managed": False})
    await device_wlan0_service.ping()

    assert wlan0.wireless is None
    assert wireless.is_connected is False
    assert eth0.connection is None
    assert connection.is_connected is False
