"""Test Network Manager Connection object."""

from unittest.mock import MagicMock, PropertyMock

from awesomeversion import AwesomeVersion
from dbus_fast import Variant
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.network import NetworkManager
from supervisor.dbus.network.interface import NetworkInterface
from supervisor.dbus.network.setting import NetworkSetting
from supervisor.dbus.network.setting.generate import get_connection_from_interface
from supervisor.host.configuration import Ip6Setting
from supervisor.host.const import InterfaceMethod
from supervisor.host.network import Interface

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.network_connection_settings import (
    ConnectionSettings as ConnectionSettingsService,
)
from tests.dbus_service_mocks.network_device import (
    ETHERNET_DEVICE_OBJECT_PATH,
    WIRELESS_DEVICE_OBJECT_PATH,
)


@pytest.fixture(name="connection_settings_service", autouse=True)
async def fixture_connection_settings_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> ConnectionSettingsService:
    """Mock Connection Settings service."""
    yield network_manager_services["network_connection_settings"]


@pytest.fixture(name="dbus_interface")
async def fixture_dbus_interface(
    dbus_session_bus: MessageBus, device_object_path: str = ETHERNET_DEVICE_OBJECT_PATH
) -> NetworkInterface:
    """Get connected dbus interface."""
    dbus_interface = NetworkInterface(device_object_path)
    await dbus_interface.connect(dbus_session_bus)
    yield dbus_interface


@pytest.mark.parametrize(
    "dbus_interface",
    [ETHERNET_DEVICE_OBJECT_PATH, WIRELESS_DEVICE_OBJECT_PATH],
    indirect=True,
)
async def test_ethernet_update(
    dbus_interface: NetworkInterface,
    connection_settings_service: ConnectionSettingsService,
    network_manager: NetworkManager,
):
    """Test network manager update."""
    connection_settings_service.Update.calls.clear()

    interface = Interface.from_dbus_interface(dbus_interface)
    conn = get_connection_from_interface(
        interface,
        network_manager,
        name=dbus_interface.settings.connection.id,
        uuid=dbus_interface.settings.connection.uuid,
    )

    await dbus_interface.settings.update(conn)

    assert len(connection_settings_service.Update.calls) == 1
    settings = connection_settings_service.Update.calls[0][0]

    assert settings["connection"]["id"] == Variant("s", "Supervisor eth0")
    assert "interface-name" not in settings["connection"]
    assert settings["connection"]["uuid"] == Variant(
        "s", "0c23631e-2118-355c-bbb0-8943229cb0d6"
    )
    assert settings["connection"]["autoconnect"] == Variant("b", True)

    assert settings["match"] == {"path": Variant("as", ["platform-ff3f0000.ethernet"])}

    assert "ipv4" in settings
    assert settings["ipv4"]["method"] == Variant("s", "auto")
    assert "gateway" not in settings["ipv4"]
    # Only DNS settings need to be preserved with auto
    assert settings["ipv4"]["dns"] == Variant("au", [16951488])
    assert "dns-data" not in settings["ipv4"]
    assert "address-data" not in settings["ipv4"]
    assert "addresses" not in settings["ipv4"]
    assert len(settings["ipv4"]["route-data"].value) == 1
    assert settings["ipv4"]["route-data"].value[0]["dest"] == Variant(
        "s", "192.168.122.0"
    )
    assert settings["ipv4"]["route-data"].value[0]["prefix"] == Variant("u", 24)
    assert settings["ipv4"]["route-data"].value[0]["next-hop"] == Variant(
        "s", "10.10.10.1"
    )
    assert settings["ipv4"]["routes"] == Variant("aau", [[8038592, 24, 17435146, 0]])

    assert "ipv6" in settings
    assert settings["ipv6"]["method"] == Variant("s", "auto")
    assert "gateway" not in settings["ipv6"]
    # Only DNS settings need to be preserved with auto
    assert settings["ipv6"]["dns"] == Variant(
        "aay", [bytearray(b" \x01H`H`\x00\x00\x00\x00\x00\x00\x00\x00\x88\x88")]
    )
    assert "dns-data" not in settings["ipv6"]
    assert "address-data" not in settings["ipv6"]
    assert "addresses" not in settings["ipv6"]
    assert settings["ipv6"]["addr-gen-mode"] == Variant("i", 0)

    assert "proxy" in settings

    assert "vlan" not in settings

    if settings["connection"]["type"] == "802-3-ethernet":
        assert "802-3-ethernet" in settings
        assert settings["802-3-ethernet"]["auto-negotiate"] == Variant("b", False)

        assert "802-11-wireless" not in settings
        assert "802-11-wireless-security" not in settings

    if settings["connection"]["type"] == "802-11-wireless":
        assert "802-11-wireless" in settings
        assert settings["802-11-wireless"]["ssid"] == Variant("ay", b"NETT")
        assert "mode" not in settings["802-11-wireless"]
        assert "powersave" not in settings["802-11-wireless"]

        assert "802-11-wireless-security" not in settings


async def test_ipv6_disabled_is_link_local(
    dbus_interface: NetworkInterface, network_manager: NetworkManager
):
    """Test disabled equals link local for ipv6."""
    interface = Interface.from_dbus_interface(dbus_interface)
    interface.ipv4setting.method = InterfaceMethod.DISABLED
    interface.ipv6setting.method = InterfaceMethod.DISABLED
    conn = get_connection_from_interface(
        interface,
        network_manager,
        name=dbus_interface.settings.connection.id,
        uuid=dbus_interface.settings.connection.uuid,
    )

    assert conn["ipv4"]["method"] == Variant("s", "disabled")
    assert conn["ipv6"]["method"] == Variant("s", "link-local")


@pytest.mark.parametrize(
    ["version", "addr_gen_mode"],
    [
        ("1.38.0", 1),
        ("1.40.0", 3),
    ],
)
async def test_ipv6_addr_gen_mode(
    dbus_interface: NetworkInterface, version: str, addr_gen_mode: int
):
    """Test addr_gen_mode with various NetworkManager versions."""
    interface = Interface.from_dbus_interface(dbus_interface)
    interface.ipv6setting = Ip6Setting(InterfaceMethod.AUTO, [], None, [])

    network_manager = MagicMock()
    type(network_manager).version = PropertyMock(return_value=AwesomeVersion(version))
    conn = get_connection_from_interface(
        interface,
        network_manager,
        name=dbus_interface.settings.connection.id,
        uuid=dbus_interface.settings.connection.uuid,
    )

    assert conn["ipv6"]["method"] == Variant("s", "auto")
    assert conn["ipv6"]["addr-gen-mode"] == Variant("i", addr_gen_mode)


async def test_watching_updated_signal(
    connection_settings_service: ConnectionSettingsService, dbus_session_bus: MessageBus
):
    """Test get settings called on update signal."""
    connection_settings_service.GetSettings.calls.clear()
    settings = NetworkSetting("/org/freedesktop/NetworkManager/Settings/1")
    await settings.connect(dbus_session_bus)

    assert connection_settings_service.GetSettings.calls == [()]

    connection_settings_service.Updated()
    await connection_settings_service.ping()
    await connection_settings_service.ping()
    assert connection_settings_service.GetSettings.calls == [(), ()]
