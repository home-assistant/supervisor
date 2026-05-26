"""Test Raspberry Pi firmware proxy."""

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.agent.boards.rpi_firmware import RPiFirmware

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.agent_boards_rpi_firmware import (
    RPiFirmware as RPiFirmwareService,
)


@pytest.fixture(name="rpi_firmware_service", autouse=True)
async def fixture_rpi_firmware_service(
    dbus_session_bus: MessageBus,
) -> RPiFirmwareService:
    """Mock Raspberry Pi firmware dbus service."""
    return (
        await mock_dbus_services({"agent_boards_rpi_firmware": None}, dbus_session_bus)
    )["agent_boards_rpi_firmware"]


async def test_dbus_rpi_firmware(
    rpi_firmware_service: RPiFirmwareService, dbus_session_bus: MessageBus
):
    """Test Raspberry Pi firmware proxy load."""
    rpi_firmware = RPiFirmware()
    await rpi_firmware.connect(dbus_session_bus)

    assert rpi_firmware.current_version == "1618412973"
    assert rpi_firmware.latest_version == "1700000000"
    assert rpi_firmware.update_available is True
    assert rpi_firmware.update_blocked is False
    assert rpi_firmware.update_pending is False
    assert rpi_firmware.blocked_reason == ""


async def test_dbus_rpi_firmware_update(
    rpi_firmware_service: RPiFirmwareService, dbus_session_bus: MessageBus
):
    """Test calling Update on the Raspberry Pi firmware proxy."""
    rpi_firmware = RPiFirmware()
    await rpi_firmware.connect(dbus_session_bus)

    assert rpi_firmware_service.update_called is False
    await rpi_firmware.update_firmware()
    await rpi_firmware_service.ping()
    assert rpi_firmware_service.update_called is True


async def test_dbus_rpi_firmware_blocked_state(
    rpi_firmware_service: RPiFirmwareService, dbus_session_bus: MessageBus
):
    """Test that blocked state is exposed via the proxy."""
    rpi_firmware_service.set_state(
        update_blocked=True, blocked_reason="unsupported_boot_device"
    )

    rpi_firmware = RPiFirmware()
    await rpi_firmware.connect(dbus_session_bus)

    assert rpi_firmware.update_blocked is True
    assert rpi_firmware.blocked_reason == "unsupported_boot_device"


async def test_dbus_rpi_firmware_update_pending(
    rpi_firmware_service: RPiFirmwareService, dbus_session_bus: MessageBus
):
    """Test that the update-pending state is exposed via the proxy."""
    rpi_firmware = RPiFirmware()
    await rpi_firmware.connect(dbus_session_bus)

    assert rpi_firmware.update_pending is False

    rpi_firmware_service.set_state(update_pending=True)
    await rpi_firmware.update()
    assert rpi_firmware.update_pending is True
