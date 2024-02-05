"""Test UDisks2 Drive."""

from datetime import UTC, datetime

from dbus_fast import Variant
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.udisks2.drive import UDisks2Drive

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.udisks2_drive import Drive as DriveService


@pytest.fixture(name="drive_ssk_storage_service")
async def fixture_drive_ssk_storage_service(
    dbus_session_bus: MessageBus,
) -> DriveService:
    """Mock SSK Storage Drive service."""
    yield (
        await mock_dbus_services(
            {
                "udisks2_drive": "/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56"
            },
            dbus_session_bus,
        )
    )["udisks2_drive"]


@pytest.fixture(name="drive_flash_disk_service")
async def fixture_drive_flash_disk_service(
    dbus_session_bus: MessageBus,
) -> DriveService:
    """Mock Flash Disk Drive service."""
    yield (
        await mock_dbus_services(
            {
                "udisks2_drive": "/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6"
            },
            dbus_session_bus,
        )
    )["udisks2_drive"]


async def test_drive_info(
    drive_ssk_storage_service: DriveService, dbus_session_bus: MessageBus
):
    """Test drive info."""
    ssk = UDisks2Drive("/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56")

    assert ssk.vendor is None
    assert ssk.model is None
    assert ssk.size is None
    assert ssk.time_detected is None
    assert ssk.ejectable is None

    await ssk.connect(dbus_session_bus)

    assert ssk.vendor == "SSK"
    assert ssk.model == "SSK Storage"
    assert ssk.size == 250059350016
    assert ssk.time_detected == datetime(2023, 2, 8, 23, 1, 44, 240492, UTC)
    assert ssk.ejectable is False

    drive_ssk_storage_service.emit_properties_changed({"Ejectable": True})
    await drive_ssk_storage_service.ping()
    assert ssk.ejectable is True

    drive_ssk_storage_service.emit_properties_changed({}, ["Ejectable"])
    await drive_ssk_storage_service.ping()
    await drive_ssk_storage_service.ping()
    assert ssk.ejectable is False


async def test_eject(
    drive_flash_disk_service: DriveService, dbus_session_bus: MessageBus
):
    """Test eject."""
    drive_flash_disk_service.Eject.calls.clear()
    flash = UDisks2Drive("/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6")
    await flash.connect(dbus_session_bus)

    await flash.eject()
    assert drive_flash_disk_service.Eject.calls == [
        ({"auth.no_user_interaction": Variant("b", True)},)
    ]
