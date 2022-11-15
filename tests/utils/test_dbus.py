"""Test dbus utility."""

from unittest.mock import AsyncMock, Mock

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.const import DBUS_OBJECT_BASE
from supervisor.exceptions import DBusFatalError, DBusInterfaceError
from supervisor.utils.dbus import DBus


async def test_missing_properties_interface(dbus_bus: MessageBus, dbus: list[str]):
    """Test introspection missing properties interface."""
    service = await DBus.connect(
        dbus_bus, "test.no.properties.interface", DBUS_OBJECT_BASE
    )
    with pytest.raises(DBusInterfaceError):
        await service.get_properties("test.no.properties.interface")


@pytest.mark.parametrize("err", [BrokenPipeError(), EOFError(), OSError()])
async def test_internal_dbus_errors(
    dbus_minimal: MessageBus,
    capture_exception: Mock,
    err: Exception,
):
    """Test internal dbus library errors become dbus error."""
    rauc = await DBus.connect(dbus_minimal, "de.pengutronix.rauc", DBUS_OBJECT_BASE)
    setattr(
        # pylint: disable=protected-access
        rauc._proxies["de.pengutronix.rauc.Installer"],
        # pylint: enable=protected-access
        "call_mark",
        proxy_mock := AsyncMock().call_mark,
    )
    proxy_mock.side_effect = err

    with pytest.raises(DBusFatalError):
        await rauc.Installer.call_mark("good", "booted")

    capture_exception.assert_called_once_with(err)
