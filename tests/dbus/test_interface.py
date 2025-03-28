"""Test dbus interface."""

import asyncio
from unittest.mock import patch

from dbus_fast.aio.message_bus import MessageBus
from dbus_fast.service import PropertyAccess, dbus_property, signal
import pytest

from supervisor.dbus.const import DBUS_OBJECT_BASE
from supervisor.dbus.interface import DBusInterface, DBusInterfaceProxy
from supervisor.exceptions import DBusInterfaceError, DBusNotConnectedError
from supervisor.utils.dbus import DBus

from tests.common import load_fixture
from tests.dbus_service_mocks.base import DBusServiceMock


class TestInterface(DBusServiceMock):
    """Test interface."""

    __test__ = False
    interface = "service.test.TestInterface"

    def __init__(self, object_path: str = "/service/test/TestInterface"):
        """Initialize object."""
        super().__init__()
        self.object_path = object_path

    @signal(name="TestSignal")
    def test_signal(self, value: str) -> "s":  # noqa: F821
        """Send test signal."""
        return value

    @dbus_property(access=PropertyAccess.READ, name="TestProp")
    def test_prop(self) -> "u":  # noqa: F821
        """Get test property."""
        return 4


class ServiceTest(DBusInterfaceProxy):
    """DBus test class."""

    bus_name = "service.test.TestInterface"
    object_path = "/service/test/TestInterface"
    properties_interface = "service.test.TestInterface"


@pytest.fixture(name="test_service")
async def fixture_test_service(dbus_session_bus: MessageBus) -> TestInterface:
    """Export test interface on dbus."""
    await dbus_session_bus.request_name("service.test.TestInterface")
    service = TestInterface()
    service.export(dbus_session_bus)
    yield service


@pytest.fixture(name="proxy")
async def fixture_proxy(
    request: pytest.FixtureRequest,
    test_service: TestInterface,
    dbus_session_bus: MessageBus,
) -> DBusInterfaceProxy:
    """Get a proxy."""
    proxy = ServiceTest()
    proxy.sync_properties = getattr(request, "param", True)
    await proxy.connect(dbus_session_bus)
    yield proxy


async def test_dbus_proxy_connect(
    proxy: DBusInterfaceProxy, test_service: TestInterface
):
    """Test dbus proxy connect."""
    assert proxy.is_connected
    assert proxy.properties["TestProp"] == 4

    test_service.emit_properties_changed({"TestProp": 1})
    await test_service.ping()
    assert proxy.properties["TestProp"] == 1

    test_service.emit_properties_changed({}, ["TestProp"])
    await test_service.ping()
    await test_service.ping()
    assert proxy.properties["TestProp"] == 4


@pytest.mark.parametrize("proxy", [False], indirect=True)
async def test_dbus_proxy_connect_no_sync(
    proxy: DBusInterfaceProxy, test_service: TestInterface
):
    """Test dbus proxy connect with no properties sync."""
    assert proxy.is_connected
    assert proxy.properties["TestProp"] == 4

    test_service.emit_properties_changed({"TestProp": 1})
    await test_service.ping()
    assert proxy.properties["TestProp"] == 4


@pytest.mark.parametrize("proxy", [False], indirect=True)
async def test_signal_listener_disconnect(
    proxy: DBusInterfaceProxy, test_service: TestInterface
):
    """Test disconnect/delete unattaches signal listeners."""
    value = None

    async def callback(val: str):
        nonlocal value
        value = val

    assert proxy.is_connected
    proxy.dbus.on_test_signal(callback)

    test_service.test_signal("hello")
    await test_service.ping()
    assert value == "hello"

    proxy.disconnect()
    test_service.test_signal("goodbye")
    await test_service.ping()
    assert value == "hello"


async def test_dbus_connected_no_raise_after_shutdown(
    test_service: TestInterface, dbus_session_bus: MessageBus
):
    """Test dbus connected methods do not raise DBusNotConnectedError after shutdown."""
    proxy = ServiceTest()
    proxy.sync_properties = False

    with pytest.raises(DBusNotConnectedError):
        await proxy.update()

    await proxy.connect(dbus_session_bus)
    assert proxy.is_connected

    proxy.shutdown()
    assert proxy.is_shutdown
    assert await proxy.update() is None


async def test_proxy_missing_properties_interface(dbus_session_bus: MessageBus):
    """Test proxy instance disconnects and errors when missing properties interface."""

    class NoPropertiesService(DBusInterfaceProxy):
        bus_name = "test.no.properties.interface"
        object_path = DBUS_OBJECT_BASE
        properties_interface = "test.no.properties.interface"

    proxy = NoPropertiesService()

    def mock_introspect(*args, **kwargs):
        """Return introspection without properties."""
        return asyncio.get_running_loop().run_in_executor(
            None, load_fixture, "test_no_properties_interface.xml"
        )

    with (
        patch.object(MessageBus, "introspect", new=mock_introspect),
        pytest.raises(DBusInterfaceError),
    ):
        await proxy.connect(dbus_session_bus)

    assert proxy.is_connected is False


async def test_initialize(test_service: TestInterface, dbus_session_bus: MessageBus):
    """Test initialize for reusing connected dbus object."""

    class ServiceTestInterfaceOnly(DBusInterface):
        bus_name = "service.test.TestInterface"
        object_path = "/service/test/TestInterface"

    proxy = ServiceTestInterfaceOnly()
    assert proxy.is_connected is False

    # Not connected
    with pytest.raises(ValueError, match="must be a connected DBus object"):
        await proxy.initialize(
            DBus(
                dbus_session_bus,
                "service.test.TestInterface",
                "/service/test/TestInterface",
            )
        )

    # Connected to wrong bus
    await dbus_session_bus.request_name("service.test.TestInterface2")
    with pytest.raises(
        ValueError,
        match="must be a DBus object connected to bus service.test.TestInterface and object /service/test/TestInterface",
    ):
        await proxy.initialize(
            await DBus.connect(
                dbus_session_bus,
                "service.test.TestInterface2",
                "/service/test/TestInterface",
            )
        )

    # Connected to wrong object
    test_service_2 = TestInterface("/service/test/TestInterface/2")
    test_service_2.export(dbus_session_bus)
    with pytest.raises(
        ValueError,
        match="must be a DBus object connected to bus service.test.TestInterface and object /service/test/TestInterface",
    ):
        await proxy.initialize(
            await DBus.connect(
                dbus_session_bus,
                "service.test.TestInterface",
                "/service/test/TestInterface/2",
            )
        )

    # Connected to correct object on the correct bus
    await proxy.initialize(
        await DBus.connect(
            dbus_session_bus,
            "service.test.TestInterface",
            "/service/test/TestInterface",
        )
    )
    assert proxy.is_connected is True


async def test_stop_sync_property_changes(
    proxy: DBusInterfaceProxy, test_service: TestInterface
):
    """Test stop sync property changes disables the sync via signal."""
    assert proxy.is_connected
    assert proxy.properties["TestProp"] == 4

    test_service.emit_properties_changed({"TestProp": 1})
    await test_service.ping()
    assert proxy.properties["TestProp"] == 1

    proxy.stop_sync_property_changes()

    test_service.emit_properties_changed({"TestProp": 4})
    await test_service.ping()
    assert proxy.properties["TestProp"] == 1
