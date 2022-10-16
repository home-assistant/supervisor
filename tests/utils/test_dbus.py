"""Test dbus utility."""
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.const import DBUS_OBJECT_BASE
from supervisor.exceptions import DBusInterfaceError
from supervisor.utils.dbus import DBus


async def test_missing_properties_interface(dbus_bus: MessageBus, dbus: list[str]):
    """Test introspection missing properties interface."""
    service = await DBus.connect(
        dbus_bus, "test.no.properties.interface", DBUS_OBJECT_BASE
    )
    with pytest.raises(DBusInterfaceError):
        await service.get_properties("test.no.properties.interface")
