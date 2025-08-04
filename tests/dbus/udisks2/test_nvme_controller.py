"""Test UDisks2 NVMe Controller."""

from datetime import UTC, datetime

from dbus_fast.aio import MessageBus
import pytest

from supervisor.dbus.udisks2.nvme_controller import UDisks2NVMeController

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.udisks2_nvme_controller import (
    NVMeController as NVMeControllerService,
)


@pytest.fixture(name="nvme_controller_service")
async def fixture_nvme_controller_service(
    dbus_session_bus: MessageBus,
) -> NVMeControllerService:
    """Mock NVMe Controller service."""
    yield (
        await mock_dbus_services(
            {
                "udisks2_nvme_controller": "/org/freedesktop/UDisks2/drives/Samsung_SSD_970_EVO_Plus_2TB_S40123456789ABC"
            },
            dbus_session_bus,
        )
    )["udisks2_nvme_controller"]


async def test_nvme_controller_info(
    nvme_controller_service: NVMeControllerService, dbus_session_bus: MessageBus
):
    """Test NVMe Controller info."""
    controller = UDisks2NVMeController(
        "/org/freedesktop/UDisks2/drives/Samsung_SSD_970_EVO_Plus_2TB_S40123456789ABC"
    )

    assert controller.state is None
    assert controller.unallocated_capacity is None
    assert controller.smart_updated is None
    assert controller.smart_temperature is None

    await controller.connect(dbus_session_bus)

    assert controller.state == "live"
    assert controller.unallocated_capacity == 0
    assert controller.smart_updated == datetime.fromtimestamp(1753906112, UTC)
    assert controller.smart_temperature == 311

    nvme_controller_service.emit_properties_changed({"SmartTemperature": 300})
    await nvme_controller_service.ping()
    await nvme_controller_service.ping()

    assert controller.smart_temperature == 300


@pytest.mark.usefixtures("nvme_controller_service")
async def test_nvme_controller_smart_get_attributes(dbus_session_bus: MessageBus):
    """Test NVMe Controller smart get attributes."""
    controller = UDisks2NVMeController(
        "/org/freedesktop/UDisks2/drives/Samsung_SSD_970_EVO_Plus_2TB_S40123456789ABC"
    )
    await controller.connect(dbus_session_bus)

    smart_log = await controller.smart_get_attributes()
    assert smart_log.available_spare == 100
    assert smart_log.percent_used == 1
    assert smart_log.total_data_read == 22890461184000
    assert smart_log.total_data_written == 27723431936000
    assert smart_log.controller_busy_minutes == 2682
    assert smart_log.temperature_sensors == [310, 305, 0, 0, 0, 0, 0, 0]
