"""Test Network Manager Connection Settings Profile Manager."""

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.network.settings import NetworkManagerSettings
from supervisor.exceptions import DBusNotConnectedError

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.network_connection_settings import SETTINGS_1_FIXTURE
from tests.dbus_service_mocks.network_settings import Settings as SettingsService


@pytest.fixture(name="settings_service")
async def fixture_settings_service(dbus_session_bus: MessageBus) -> SettingsService:
    """Mock Settings service."""
    yield (
        await mock_dbus_services(
            {"network_settings": None, "network_connection_settings": None},
            dbus_session_bus,
        )
    )["network_settings"]


async def test_add_connection(
    settings_service: SettingsService, dbus_session_bus: MessageBus
):
    """Test adding settings connection."""
    settings_service.AddConnection.calls.clear()
    settings = NetworkManagerSettings()

    with pytest.raises(DBusNotConnectedError):
        await settings.add_connection(SETTINGS_1_FIXTURE)

    await settings.connect(dbus_session_bus)

    connection_settings = await settings.add_connection(SETTINGS_1_FIXTURE)
    assert connection_settings.connection.uuid == "0c23631e-2118-355c-bbb0-8943229cb0d6"
    assert connection_settings.ipv4.method == "auto"

    assert settings_service.AddConnection.calls == [(SETTINGS_1_FIXTURE,)]


async def test_reload_connections(
    settings_service: SettingsService, dbus_session_bus: MessageBus
):
    """Test reload connections."""
    settings_service.ReloadConnections.calls.clear()
    settings = NetworkManagerSettings()

    with pytest.raises(DBusNotConnectedError):
        await settings.reload_connections()

    await settings.connect(dbus_session_bus)

    assert await settings.reload_connections() is True
    assert settings_service.ReloadConnections.calls == [()]


async def test_dbus_network_settings_connect_error(
    dbus_session_bus: MessageBus, caplog: pytest.LogCaptureFixture
):
    """Test connecting to network settings error."""
    settings = NetworkManagerSettings()
    await settings.connect(dbus_session_bus)
    assert "No Network Manager Settings support on the host" in caplog.text
