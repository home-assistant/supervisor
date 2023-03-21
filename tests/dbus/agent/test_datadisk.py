"""Test Datadisk/Agent dbus interface."""
# pylint: disable=import-error
from pathlib import Path

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.agent import OSAgent
from supervisor.exceptions import DBusNotConnectedError

from tests.dbus_service_mocks.agent_datadisk import DataDisk as DataDiskService
from tests.dbus_service_mocks.base import DBusServiceMock


@pytest.fixture(name="datadisk_service", autouse=True)
async def fixture_datadisk_service(
    os_agent_services: dict[str, DBusServiceMock]
) -> DataDiskService:
    """Mock DataDisk dbus service."""
    yield os_agent_services["agent_datadisk"]


async def test_dbus_osagent_datadisk(
    datadisk_service: DataDiskService, dbus_session_bus: MessageBus
):
    """Test OS-Agent datadisk properties."""
    os_agent = OSAgent()

    assert os_agent.datadisk.current_device is None

    await os_agent.connect(dbus_session_bus)

    assert os_agent.datadisk.current_device.as_posix() == "/dev/sda"

    datadisk_service.emit_properties_changed({"CurrentDevice": "/dev/sda1"})
    await datadisk_service.ping()
    assert os_agent.datadisk.current_device.as_posix() == "/dev/sda1"

    datadisk_service.emit_properties_changed({}, ["CurrentDevice"])
    await datadisk_service.ping()
    await datadisk_service.ping()
    assert os_agent.datadisk.current_device.as_posix() == "/dev/sda"


async def test_dbus_osagent_datadisk_change_device(
    datadisk_service: DataDiskService, dbus_session_bus: MessageBus
):
    """Change datadisk on device."""
    datadisk_service.ChangeDevice.calls.clear()
    os_agent = OSAgent()

    with pytest.raises(DBusNotConnectedError):
        await os_agent.datadisk.change_device(Path("/dev/sdb"))

    await os_agent.connect(dbus_session_bus)

    assert await os_agent.datadisk.change_device(Path("/dev/sdb")) is None
    assert datadisk_service.ChangeDevice.calls == [("/dev/sdb",)]


async def test_dbus_osagent_datadisk_reload_device(
    datadisk_service: DataDiskService, dbus_session_bus: MessageBus
):
    """Change datadisk on device."""
    datadisk_service.ReloadDevice.calls.clear()
    os_agent = OSAgent()

    with pytest.raises(DBusNotConnectedError):
        await os_agent.datadisk.reload_device()

    await os_agent.connect(dbus_session_bus)

    assert await os_agent.datadisk.reload_device() is None
    assert datadisk_service.ReloadDevice.calls == [tuple()]
