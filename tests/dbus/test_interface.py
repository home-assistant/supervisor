"""Test dbus interface."""

import asyncio
from dataclasses import dataclass
from unittest.mock import MagicMock

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.interface import DBusInterfaceProxy

from tests.common import fire_property_change_signal, fire_watched_signal


@dataclass
class DBusInterfaceProxyMock:
    """DBus Interface and signalling mocks."""

    obj: DBusInterfaceProxy
    on_device_added: MagicMock = MagicMock()
    off_device_added: MagicMock = MagicMock()


@pytest.fixture(name="proxy")
async def fixture_proxy(
    request: pytest.FixtureRequest, dbus_bus: MessageBus, dbus
) -> DBusInterfaceProxyMock:
    """Get a proxy."""
    proxy = DBusInterfaceProxy()
    proxy.bus_name = "org.freedesktop.NetworkManager"
    proxy.object_path = "/org/freedesktop/NetworkManager"
    proxy.properties_interface = "org.freedesktop.NetworkManager"
    proxy.sync_properties = request.param

    await proxy.connect(dbus_bus)

    # pylint: disable=protected-access
    nm_proxy = proxy.dbus._proxies["org.freedesktop.NetworkManager"]

    mock = DBusInterfaceProxyMock(proxy)
    setattr(nm_proxy, "on_device_added", mock.on_device_added)
    setattr(nm_proxy, "off_device_added", mock.off_device_added)

    yield mock


@pytest.mark.parametrize("proxy", [True], indirect=True)
async def test_dbus_proxy_connect(proxy: DBusInterfaceProxyMock):
    """Test dbus proxy connect."""
    assert proxy.obj.is_connected
    assert proxy.obj.properties["Connectivity"] == 4

    fire_property_change_signal(proxy.obj, {"Connectivity": 1})
    await asyncio.sleep(0)
    assert proxy.obj.properties["Connectivity"] == 1


@pytest.mark.parametrize("proxy", [False], indirect=True)
async def test_dbus_proxy_connect_no_sync(proxy: DBusInterfaceProxyMock):
    """Test dbus proxy connect with no properties sync."""
    assert proxy.obj.is_connected
    assert proxy.obj.properties["Connectivity"] == 4

    with pytest.raises(AssertionError):
        fire_property_change_signal(proxy.obj, {"Connectivity": 1})


@pytest.mark.parametrize("proxy", [False], indirect=True)
async def test_signal_listener_disconnect(proxy: DBusInterfaceProxyMock):
    """Test disconnect/delete unattaches signal listeners."""
    assert proxy.obj.is_connected
    device = None

    async def callback(dev: str):
        nonlocal device
        device = dev

    proxy.obj.dbus.on_device_added(callback)
    proxy.on_device_added.assert_called_once_with(callback, unpack_variants=True)

    fire_watched_signal(
        proxy.obj, "org.freedesktop.NetworkManager.DeviceAdded", ["/test/obj/1"]
    )
    await asyncio.sleep(0)
    assert device == "/test/obj/1"

    proxy.obj.disconnect()
    proxy.off_device_added.assert_called_once_with(callback, unpack_variants=True)


@pytest.mark.parametrize("proxy", [False], indirect=True)
async def test_dbus_proxy_shutdown_pending_task(proxy: DBusInterfaceProxyMock):
    """Test pending task does not raise DBusNotConnectedError after shutdown."""
    assert proxy.obj.is_connected
    device = None

    async def callback(dev: str):
        nonlocal device
        await proxy.obj.update()
        device = dev

    proxy.obj.dbus.on_device_added(callback)
    fire_watched_signal(
        proxy.obj, "org.freedesktop.NetworkManager.DeviceAdded", ["/test/obj/1"]
    )
    proxy.obj.shutdown()
    await asyncio.sleep(0)
    assert device == "/test/obj/1"
