"""Test UDisks2 Drive."""

import asyncio
from datetime import datetime, timezone

from dbus_fast.aio.message_bus import MessageBus

from supervisor.dbus.udisks2.drive import UDisks2Drive

from tests.common import fire_property_change_signal


async def test_drive_info(dbus: list[str], dbus_bus: MessageBus):
    """Test drive info."""
    ssk = UDisks2Drive("/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56")

    assert ssk.vendor is None
    assert ssk.model is None
    assert ssk.size is None
    assert ssk.time_detected is None
    assert ssk.ejectable is None

    await ssk.connect(dbus_bus)

    assert ssk.vendor == "SSK"
    assert ssk.model == "SSK Storage"
    assert ssk.size == 250059350016
    assert ssk.time_detected == datetime(2023, 2, 8, 23, 1, 44, 240492, timezone.utc)
    assert ssk.ejectable is False

    fire_property_change_signal(ssk, {"Ejectable": True})
    await asyncio.sleep(0)
    assert ssk.ejectable is True


async def test_eject(dbus: list[str], dbus_bus: MessageBus):
    """Test eject."""
    flash = UDisks2Drive("/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6")
    await flash.connect(dbus_bus)

    await flash.eject()
    assert dbus == [
        "/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6-org.freedesktop.UDisks2.Drive.Eject"
    ]
