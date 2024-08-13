"""Test AppArmor/Agent dbus interface."""

# pylint: disable=import-error
from pathlib import Path

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.agent import OSAgent
from supervisor.exceptions import DBusNotConnectedError

from tests.dbus_service_mocks.agent_apparmor import AppArmor as AppArmorService
from tests.dbus_service_mocks.base import DBusServiceMock


@pytest.fixture(name="apparmor_service", autouse=True)
async def fixture_apparmor_service(
    os_agent_services: dict[str, DBusServiceMock],
) -> AppArmorService:
    """Mock AppArmor dbus service."""
    yield os_agent_services["agent_apparmor"]


async def test_dbus_osagent_apparmor(
    apparmor_service: AppArmorService, dbus_session_bus: MessageBus
):
    """Test AppArmor properties."""
    os_agent = OSAgent()

    assert os_agent.apparmor.version is None

    await os_agent.connect(dbus_session_bus)

    assert os_agent.apparmor.version == "2.13.2"

    apparmor_service.emit_properties_changed({"ParserVersion": "1.0.0"})
    await apparmor_service.ping()
    assert os_agent.apparmor.version == "1.0.0"

    apparmor_service.emit_properties_changed({}, ["ParserVersion"])
    await apparmor_service.ping()
    await apparmor_service.ping()
    assert os_agent.apparmor.version == "2.13.2"


async def test_dbus_osagent_apparmor_load(
    apparmor_service: AppArmorService, dbus_session_bus: MessageBus
):
    """Load AppArmor Profile on host."""
    apparmor_service.LoadProfile.calls.clear()
    os_agent = OSAgent()

    with pytest.raises(DBusNotConnectedError):
        await os_agent.apparmor.load_profile(
            Path("/data/apparmor/profile"), Path("/data/apparmor/cache")
        )

    await os_agent.connect(dbus_session_bus)

    assert (
        await os_agent.apparmor.load_profile(
            Path("/data/apparmor/profile"), Path("/data/apparmor/cache")
        )
        is None
    )
    assert apparmor_service.LoadProfile.calls == [
        ("/data/apparmor/profile", "/data/apparmor/cache")
    ]


async def test_dbus_osagent_apparmor_unload(
    apparmor_service: AppArmorService, dbus_session_bus: MessageBus
):
    """Unload AppArmor Profile on host."""
    apparmor_service.UnloadProfile.calls.clear()
    os_agent = OSAgent()

    with pytest.raises(DBusNotConnectedError):
        await os_agent.apparmor.unload_profile(
            Path("/data/apparmor/profile"), Path("/data/apparmor/cache")
        )

    await os_agent.connect(dbus_session_bus)

    assert (
        await os_agent.apparmor.unload_profile(
            Path("/data/apparmor/profile"), Path("/data/apparmor/cache")
        )
        is None
    )
    assert apparmor_service.UnloadProfile.calls == [
        ("/data/apparmor/profile", "/data/apparmor/cache")
    ]
