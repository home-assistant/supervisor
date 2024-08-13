"""Test hostname dbus interface."""

# pylint: disable=import-error
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.hostname import Hostname
from supervisor.exceptions import DBusNotConnectedError

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.hostname import Hostname as HostnameService


@pytest.fixture(name="hostname_service")
async def fixture_hostname_service(dbus_session_bus: MessageBus) -> HostnameService:
    """Mock hostname dbus service."""
    yield (await mock_dbus_services({"hostname": None}, dbus_session_bus))["hostname"]


async def test_dbus_hostname_info(
    hostname_service: HostnameService, dbus_session_bus: MessageBus
):
    """Test hostname properties."""
    hostname = Hostname()

    assert hostname.hostname is None

    await hostname.connect(dbus_session_bus)

    assert hostname.hostname == "homeassistant-n2"
    assert hostname.kernel == "5.10.33"
    assert (
        hostname.cpe
        == "cpe:2.3:o:home-assistant:haos:6.0.dev20210504:*:development:*:*:*:odroid-n2:*"
    )
    assert hostname.operating_system == "Home Assistant OS 6.0.dev20210504"

    hostname_service.emit_properties_changed({"StaticHostname": "test"})
    await hostname_service.ping()
    assert hostname.hostname == "test"

    hostname_service.emit_properties_changed({}, ["StaticHostname"])
    await hostname_service.ping()
    await hostname_service.ping()  # To process the follow-up get all properties call
    assert hostname.hostname == "homeassistant-n2"


async def test_dbus_sethostname(
    hostname_service: HostnameService, dbus_session_bus: MessageBus
):
    """Set hostname on backend."""
    hostname_service.SetStaticHostname.calls.clear()
    hostname = Hostname()

    with pytest.raises(DBusNotConnectedError):
        await hostname.set_static_hostname("StarWars")

    await hostname.connect(dbus_session_bus)

    assert hostname.hostname == "homeassistant-n2"
    await hostname.set_static_hostname("StarWars")
    assert hostname_service.SetStaticHostname.calls == [("StarWars", False)]
    await hostname_service.ping()
    assert hostname.hostname == "StarWars"


async def test_dbus_hostname_connect_error(
    dbus_session_bus: MessageBus, caplog: pytest.LogCaptureFixture
):
    """Test connecting to hostname error."""
    hostname = Hostname()
    await hostname.connect(dbus_session_bus)
    assert "No hostname support on the host" in caplog.text
