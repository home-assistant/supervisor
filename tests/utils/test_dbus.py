"""Test dbus utility."""

from unittest.mock import AsyncMock, Mock, patch

from dbus_fast.aio.message_bus import MessageBus
from dbus_fast.service import method
import pytest

from supervisor.dbus.const import DBUS_OBJECT_BASE
from supervisor.exceptions import DBusFatalError, DBusInterfaceError
from supervisor.utils.dbus import DBus

from tests.common import load_fixture
from tests.dbus_service_mocks.base import DBusServiceMock


class TestInterface(DBusServiceMock):
    """Test interface."""

    interface = "service.test.TestInterface"
    object_path = DBUS_OBJECT_BASE

    @method(name="Test")
    def test(self, _: "b") -> None:  # noqa: F821
        """Do Test method."""


@pytest.fixture(name="test_service")
async def fixture_test_service(dbus_session_bus: MessageBus) -> TestInterface:
    """Export test interface on dbus."""
    await dbus_session_bus.request_name("service.test.TestInterface")
    service = TestInterface()
    service.export(dbus_session_bus)
    yield service


async def test_missing_properties_interface(dbus_session_bus: MessageBus):
    """Test introspection missing properties interface."""

    async def mock_introspect(*args, **kwargs):
        """Return introspection without properties."""
        return load_fixture("test_no_properties_interface.xml")

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
