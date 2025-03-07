"""Test dbus utility."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

from dbus_fast import ErrorType
from dbus_fast.aio.message_bus import MessageBus
from dbus_fast.errors import DBusError as DBusFastDBusError
from dbus_fast.service import method, signal
import pytest

from supervisor.dbus.const import DBUS_OBJECT_BASE
from supervisor.exceptions import (
    DBusFatalError,
    DBusInterfaceError,
    DBusServiceUnkownError,
)
from supervisor.utils.dbus import DBus

from tests.common import load_fixture
from tests.dbus_service_mocks.base import DBusServiceMock


class TestInterface(DBusServiceMock):
    """Test interface."""

    __test__ = False
    interface = "service.test.TestInterface"
    object_path = DBUS_OBJECT_BASE

    @method(name="Test")
    def test(self, _: "b") -> None:  # noqa: F821
        """Do Test method."""

    @signal(name="Test")
    def signal_test(self) -> None:
        """Signal Test."""


@pytest.fixture(name="test_service")
async def fixture_test_service(dbus_session_bus: MessageBus) -> TestInterface:
    """Export test interface on dbus."""
    await dbus_session_bus.request_name("service.test.TestInterface")
    service = TestInterface()
    service.export(dbus_session_bus)
    yield service


async def test_missing_properties_interface(dbus_session_bus: MessageBus):
    """Test introspection missing properties interface."""

    def mock_introspect(*args, **kwargs):
        """Return introspection without properties."""
        return asyncio.get_running_loop().run_in_executor(
            None, load_fixture, "test_no_properties_interface.xml"
        )

    with patch.object(MessageBus, "introspect", new=mock_introspect):
        service = await DBus.connect(
            dbus_session_bus, "test.no.properties.interface", DBUS_OBJECT_BASE
        )

    with pytest.raises(DBusInterfaceError):
        await service.get_properties("test.no.properties.interface")


@pytest.mark.parametrize("err", [BrokenPipeError(), EOFError(), OSError()])
async def test_internal_dbus_errors(
    test_service: TestInterface,
    dbus_session_bus: MessageBus,
    capture_exception: Mock,
    err: Exception,
):
    """Test internal dbus library errors become dbus error."""
    test_obj = await DBus.connect(
        dbus_session_bus, "service.test.TestInterface", DBUS_OBJECT_BASE
    )
    setattr(
        # pylint: disable=protected-access
        test_obj._proxies["service.test.TestInterface"],
        # pylint: enable=protected-access
        "call_test",
        proxy_mock := AsyncMock().call_test,
    )
    proxy_mock.side_effect = err

    with pytest.raises(DBusFatalError):
        await test_obj.call_test(True)

    capture_exception.assert_called_once_with(err)


async def test_introspect(test_service: TestInterface, dbus_session_bus: MessageBus):
    """Test introspect of dbus object."""
    test_obj = DBus(dbus_session_bus, "service.test.TestInterface", DBUS_OBJECT_BASE)

    introspection = await test_obj.introspect()

    assert {"service.test.TestInterface", "org.freedesktop.DBus.Properties"} <= {
        interface.name for interface in introspection.interfaces
    }
    test_interface = next(
        interface
        for interface in introspection.interfaces
        if interface.name == "service.test.TestInterface"
    )
    assert "Test" in {method_.name for method_ in test_interface.methods}


async def test_init_proxy(test_service: TestInterface, dbus_session_bus: MessageBus):
    """Test init proxy on already connected object to update interfaces."""
    test_obj = await DBus.connect(
        dbus_session_bus, "service.test.TestInterface", DBUS_OBJECT_BASE
    )
    orig_introspection = await test_obj.introspect()
    callback_count = 0

    def test_callback():
        nonlocal callback_count
        callback_count += 1

    class TestInterface2(TestInterface):
        """Test interface 2."""

        interface = "service.test.TestInterface.Test2"
        object_path = DBUS_OBJECT_BASE

    # Test interfaces and methods match expected
    assert "service.test.TestInterface" in test_obj.proxies
    assert await test_obj.call_test(True) is None
    assert "service.test.TestInterface.Test2" not in test_obj.proxies

    # Test basic signal listening works
    test_obj.on_test(test_callback)
    test_service.signal_test()
    await test_service.ping()
    assert callback_count == 1
    callback_count = 0

    # Export the second interface and re-create proxy
    test_service_2 = TestInterface2()
    test_service_2.export(dbus_session_bus)

    await test_obj.init_proxy()

    # Test interfaces and methods match expected
    assert "service.test.TestInterface" in test_obj.proxies
    assert await test_obj.call_test(True) is None
    assert "service.test.TestInterface.Test2" in test_obj.proxies
    assert await test_obj.Test2.call_test(True) is None

    # Test signal listening. First listener should still be attached
    test_obj.Test2.on_test(test_callback)
    test_service_2.signal_test()
    await test_service_2.ping()
    assert callback_count == 1

    test_service.signal_test()
    await test_service.ping()
    assert callback_count == 2
    callback_count = 0

    # Return to original introspection and test interfaces have reset
    await test_obj.init_proxy(introspection=orig_introspection)

    assert "service.test.TestInterface" in test_obj.proxies
    assert "service.test.TestInterface.Test2" not in test_obj.proxies

    # Signal listener for second interface should disconnect, first remains
    test_service_2.signal_test()
    await test_service_2.ping()
    assert callback_count == 0

    test_service.signal_test()
    await test_service.ping()
    assert callback_count == 1
    callback_count = 0

    # Should be able to disconnect first signal listener on new proxy obj
    test_obj.off_test(test_callback)
    test_service.signal_test()
    await test_service.ping()
    assert callback_count == 0


def test_from_dbus_error():
    """Test converting DBus fast errors to Supervisor specific errors."""
    dbus_fast_error = DBusFastDBusError(
        ErrorType.SERVICE_UNKNOWN, "The name is not activatable"
    )

    assert type(DBus.from_dbus_error(dbus_fast_error)) is DBusServiceUnkownError
