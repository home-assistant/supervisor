"""Test network manager."""
import asyncio
from ipaddress import IPv4Address, IPv6Address
from unittest.mock import Mock, PropertyMock, patch

from dbus_fast.aio.proxy_object import ProxyInterface
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.dbus.const import ConnectionStateFlags, InterfaceMethod
from supervisor.exceptions import DBusFatalError, HostNotSupportedError
from supervisor.homeassistant.const import WSEvent, WSType
from supervisor.host.const import InterfaceType, WifiMode
from supervisor.host.network import Interface, IpConfig
from supervisor.utils.dbus import DBus

from tests.common import fire_property_change_signal


async def test_load(coresys: CoreSys, dbus: list[str]):
    """Test network manager load."""
    dbus.clear()
    await coresys.host.network.load()

    assert coresys.host.network.connectivity is True

    assert len(coresys.host.network.dns_servers) == 1
    assert str(coresys.host.network.dns_servers[0]) == "192.168.30.1"

    assert len(coresys.host.network.interfaces) == 2
    assert coresys.host.network.interfaces[0].name == "eth0"
    assert coresys.host.network.interfaces[0].enabled is True
    assert coresys.host.network.interfaces[0].ipv4.method == InterfaceMethod.AUTO
    assert coresys.host.network.interfaces[0].ipv4.gateway == IPv4Address("192.168.2.1")
    assert coresys.host.network.interfaces[0].ipv4.ready is True
    assert coresys.host.network.interfaces[0].ipv6.method == InterfaceMethod.AUTO
    assert coresys.host.network.interfaces[0].ipv6.gateway == IPv6Address(
        "fe80::da58:d7ff:fe00:9c69"
    )
    assert coresys.host.network.interfaces[0].ipv6.ready is True
    assert coresys.host.network.interfaces[1].name == "wlan0"
    assert coresys.host.network.interfaces[1].enabled is False

    assert (
        "/org/freedesktop/NetworkManager-org.freedesktop.NetworkManager.ActivateConnection"
        in dbus
    )
    assert (
        "/org/freedesktop/NetworkManager-org.freedesktop.NetworkManager.Connectivity"
        in dbus
    )
    assert (
        "/org/freedesktop/NetworkManager-org.freedesktop.NetworkManager.CheckConnectivity"
        not in dbus
    )


async def test_load_with_disabled_methods(coresys: CoreSys):
    """Test load does not disable methods of interfaces."""
    with patch(
        "supervisor.host.network.Interface.from_dbus_interface",
        return_value=Interface(
            "eth0",
            True,
            False,
            False,
            InterfaceType.ETHERNET,
            IpConfig(InterfaceMethod.DISABLED, [], None, [], False),
            IpConfig(InterfaceMethod.DISABLED, [], None, [], False),
            None,
            None,
        ),
    ), patch.object(
        coresys.host.sys_dbus.network,
        "activate_connection",
        new=Mock(wraps=coresys.host.sys_dbus.network.activate_connection),
    ) as activate_connection:
        await coresys.host.network.load()

        activate_connection.assert_not_called()


async def test_load_with_network_connection_issues(coresys: CoreSys, dbus: list[str]):
    """Test load does not update interfaces with network connection issues."""
    with patch(
        "supervisor.dbus.network.connection.NetworkConnection.state_flags",
        new=PropertyMock(return_value={ConnectionStateFlags.IP6_READY}),
    ), patch(
        "supervisor.dbus.network.connection.NetworkConnection.ipv4",
        new=PropertyMock(return_value=None),
    ):
        dbus.clear()
        await coresys.host.network.load()

        assert (
            "/org/freedesktop/NetworkManager-org.freedesktop.NetworkManager.ActivateConnection"
            not in dbus
        )

        assert len(coresys.host.network.interfaces) == 2
        assert coresys.host.network.interfaces[0].name == "eth0"
        assert coresys.host.network.interfaces[0].enabled is True
        assert coresys.host.network.interfaces[0].ipv4.method == InterfaceMethod.AUTO
        assert coresys.host.network.interfaces[0].ipv4.gateway is None
        assert coresys.host.network.interfaces[0].ipv6.method == InterfaceMethod.AUTO
        assert coresys.host.network.interfaces[0].ipv6.gateway == IPv6Address(
            "fe80::da58:d7ff:fe00:9c69"
        )


async def test_scan_wifi(coresys: CoreSys):
    """Test scanning wifi."""
    with pytest.raises(HostNotSupportedError):
        await coresys.host.network.scan_wifi(coresys.host.network.get("eth0"))

    with patch("supervisor.host.network.asyncio.sleep"):
        aps = await coresys.host.network.scan_wifi(coresys.host.network.get("wlan0"))

    assert len(aps) == 2
    assert aps[0].mac == "E4:57:40:A9:D7:DE"
    assert aps[0].mode == WifiMode.INFRASTRUCTURE
    assert aps[1].mac == "18:4B:0D:23:A1:9C"
    assert aps[1].mode == WifiMode.INFRASTRUCTURE


async def test_scan_wifi_with_failures(coresys: CoreSys, caplog):
    """Test scanning wifi with accesspoint processing failures."""
    # pylint: disable=protected-access
    init_proxy = DBus._init_proxy
    call_dbus = DBus.call_dbus

    async def mock_init_proxy(self):
        if self.object_path != "/org/freedesktop/NetworkManager/AccessPoint/99999":
            return await init_proxy(self)

        raise DBusFatalError("Fail")

    async def mock_call_dbus(
        proxy_interface: ProxyInterface,
        method: str,
        *args,
        remove_signature: bool = True,
    ):
        if method == "call_get_all_access_points":
            return [
                "/org/freedesktop/NetworkManager/AccessPoint/43099",
                "/org/freedesktop/NetworkManager/AccessPoint/43100",
                "/org/freedesktop/NetworkManager/AccessPoint/99999",
            ]

        return await call_dbus(
            proxy_interface, method, *args, remove_signature=remove_signature
        )

    with patch("supervisor.host.network.asyncio.sleep"), patch(
        "supervisor.utils.dbus.DBus.call_dbus", new=mock_call_dbus
    ), patch.object(DBus, "_init_proxy", new=mock_init_proxy):
        aps = await coresys.host.network.scan_wifi(coresys.host.network.get("wlan0"))
        assert len(aps) == 2

    assert "Can't process an AP" in caplog.text


async def test_host_connectivity_changed(coresys: CoreSys):
    """Test host connectivity changed."""
    # pylint: disable=protected-access
    client = coresys.homeassistant.websocket._client
    await coresys.host.network.load()

    assert coresys.host.network.connectivity is True

    fire_property_change_signal(coresys.dbus.network, {"Connectivity": 1})
    await asyncio.sleep(0)
    assert coresys.host.network.connectivity is False
    await asyncio.sleep(0)
    client.async_send_command.assert_called_once_with(
        {
            "type": WSType.SUPERVISOR_EVENT,
            "data": {
                "event": WSEvent.SUPERVISOR_UPDATE,
                "update_key": "network",
                "data": {"host_internet": False},
            },
        }
    )

    client.async_send_command.reset_mock()
    fire_property_change_signal(coresys.dbus.network, {}, ["Connectivity"])
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert coresys.host.network.connectivity is True
    await asyncio.sleep(0)
    client.async_send_command.assert_called_once_with(
        {
            "type": WSType.SUPERVISOR_EVENT,
            "data": {
                "event": WSEvent.SUPERVISOR_UPDATE,
                "update_key": "network",
                "data": {"host_internet": True},
            },
        }
    )


async def test_host_connectivity_disabled(coresys: CoreSys):
    """Test host connectivity check disabled."""
    # pylint: disable=protected-access
    client = coresys.homeassistant.websocket._client
    await coresys.host.network.load()

    coresys.core.state = CoreState.RUNNING
    await asyncio.sleep(0)
    client.async_send_command.reset_mock()

    assert "connectivity_check" not in coresys.resolution.unsupported
    assert coresys.host.network.connectivity is True

    fire_property_change_signal(
        coresys.dbus.network, {"ConnectivityCheckEnabled": False}
    )
    await asyncio.sleep(0)
    assert coresys.host.network.connectivity is None
    await asyncio.sleep(0)
    client.async_send_command.assert_called_once_with(
        {
            "type": WSType.SUPERVISOR_EVENT,
            "data": {
                "event": WSEvent.SUPERVISOR_UPDATE,
                "update_key": "network",
                "data": {"host_internet": None},
            },
        }
    )
    assert "connectivity_check" in coresys.resolution.unsupported

    client.async_send_command.reset_mock()
    fire_property_change_signal(coresys.dbus.network, {}, ["ConnectivityCheckEnabled"])
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert coresys.host.network.connectivity is True
    await asyncio.sleep(0)
    client.async_send_command.assert_called_once_with(
        {
            "type": WSType.SUPERVISOR_EVENT,
            "data": {
                "event": WSEvent.SUPERVISOR_UPDATE,
                "update_key": "network",
                "data": {"host_internet": True},
            },
        }
    )
    assert "connectivity_check" not in coresys.resolution.unsupported
