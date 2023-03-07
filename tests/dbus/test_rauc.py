"""Test rauc dbus interface."""
# pylint: disable=import-error
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.const import RaucState
from supervisor.dbus.rauc import Rauc
from supervisor.exceptions import DBusNotConnectedError

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.rauc import Rauc as RaucService


@pytest.fixture(name="rauc_service", autouse=True)
async def fixture_rauc_service(dbus_session_bus: MessageBus) -> RaucService:
    """Mock rauc dbus service."""
    yield (await mock_dbus_services({"rauc": None}, dbus_session_bus))["rauc"]


async def test_rauc_info(rauc_service: RaucService, dbus_session_bus: MessageBus):
    """Test rauc properties."""
    rauc = Rauc()

    assert rauc.boot_slot is None
    assert rauc.operation is None
    assert rauc.last_error is None

    await rauc.connect(dbus_session_bus)

    assert rauc.boot_slot == "B"
    assert rauc.operation == "idle"
    assert rauc.last_error == ""

    rauc_service.emit_properties_changed({"LastError": "Error!"})
    await rauc_service.ping()
    assert rauc.last_error == "Error!"

    rauc_service.emit_properties_changed({}, ["LastError"])
    await rauc_service.ping()
    await rauc_service.ping()  # To process the follow-up get all properties call
    assert rauc.last_error == ""


async def test_install(dbus_session_bus: MessageBus):
    """Test install."""
    rauc = Rauc()

    with pytest.raises(DBusNotConnectedError):
        await rauc.install("rauc_file")

    await rauc.connect(dbus_session_bus)

    async with rauc.signal_completed() as signal:
        assert await rauc.install("rauc_file") is None
        assert await signal.wait_for_signal() == [0]


async def test_get_slot_status(dbus_session_bus: MessageBus):
    """Test get slot status."""
    rauc = Rauc()

    with pytest.raises(DBusNotConnectedError):
        await rauc.get_slot_status()

    await rauc.connect(dbus_session_bus)

    slot_status = await rauc.get_slot_status()
    assert len(slot_status) == 6
    assert slot_status[0][0] == "kernel.0"
    assert slot_status[0][1]["boot-status"] == "good"
    assert slot_status[0][1]["device"] == "/dev/disk/by-partlabel/hassos-kernel0"
    assert slot_status[0][1]["bootname"] == "A"
    assert slot_status[4][0] == "kernel.1"
    assert slot_status[4][1]["boot-status"] == "good"
    assert slot_status[4][1]["device"] == "/dev/disk/by-partlabel/hassos-kernel1"
    assert slot_status[4][1]["bootname"] == "B"


async def test_mark(dbus_session_bus: MessageBus):
    """Test mark."""
    rauc = Rauc()

    with pytest.raises(DBusNotConnectedError):
        await rauc.mark(RaucState.GOOD, "booted")

    await rauc.connect(dbus_session_bus)

    mark = await rauc.mark(RaucState.GOOD, "booted")
    assert mark[0] == "kernel.1"
    assert mark[1] == "marked slot kernel.1 as good"
