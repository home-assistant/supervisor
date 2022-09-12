"""Test rauc dbus interface."""
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import RaucState
from supervisor.exceptions import DBusNotConnectedError


async def test_rauc(coresys: CoreSys):
    """Test rauc properties."""
    assert coresys.dbus.rauc.boot_slot is None
    assert coresys.dbus.rauc.operation is None

    await coresys.dbus.rauc.connect(coresys.dbus.bus)
    await coresys.dbus.rauc.update()

    assert coresys.dbus.rauc.boot_slot == "B"
    assert coresys.dbus.rauc.operation == "idle"


async def test_install(coresys: CoreSys, dbus: list[str]):
    """Test install."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.rauc.install("rauc_file")

    await coresys.dbus.rauc.connect(coresys.dbus.bus)

    dbus.clear()
    async with coresys.dbus.rauc.signal_completed() as signal:
        assert await coresys.dbus.rauc.install("rauc_file") is None
        assert await signal.wait_for_signal() == [0]

    assert dbus == ["/-de.pengutronix.rauc.Installer.Install"]


async def test_get_slot_status(coresys: CoreSys, dbus: list[str]):
    """Test get slot status."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.rauc.get_slot_status()

    await coresys.dbus.rauc.connect(coresys.dbus.bus)

    dbus.clear()
    slot_status = await coresys.dbus.rauc.get_slot_status()
    assert len(slot_status) == 6
    assert slot_status[0][0] == "kernel.0"
    assert slot_status[0][1]["boot-status"] == "good"
    assert slot_status[0][1]["device"] == "/dev/disk/by-partlabel/hassos-kernel0"
    assert slot_status[0][1]["bootname"] == "A"
    assert slot_status[4][0] == "kernel.1"
    assert slot_status[4][1]["boot-status"] == "good"
    assert slot_status[4][1]["device"] == "/dev/disk/by-partlabel/hassos-kernel1"
    assert slot_status[4][1]["bootname"] == "B"
    assert dbus == ["/-de.pengutronix.rauc.Installer.GetSlotStatus"]


async def test_mark(coresys: CoreSys, dbus: list[str]):
    """Test mark."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.rauc.mark(RaucState.GOOD, "booted")

    await coresys.dbus.rauc.connect(coresys.dbus.bus)

    dbus.clear()
    mark = await coresys.dbus.rauc.mark(RaucState.GOOD, "booted")
    assert mark[0] == "kernel.1"
    assert mark[1] == "marked slot kernel.1 as good"
    assert dbus == ["/-de.pengutronix.rauc.Installer.Mark"]
