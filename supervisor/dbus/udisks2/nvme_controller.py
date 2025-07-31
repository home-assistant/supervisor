"""Interface to UDisks2 NVME Controller over D-Bus."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, cast

from dbus_fast.aio import MessageBus

from ..const import (
    DBUS_ATTR_CONTROLLER_ID,
    DBUS_ATTR_FGUID,
    DBUS_ATTR_NVME_REVISION,
    DBUS_ATTR_SANITIZE_PERCENT_REMAINING,
    DBUS_ATTR_SANITIZE_STATUS,
    DBUS_ATTR_SMART_CRITICAL_WARNING,
    DBUS_ATTR_SMART_POWER_ON_HOURS,
    DBUS_ATTR_SMART_SELFTEST_PERCENT_REMAINING,
    DBUS_ATTR_SMART_SELFTEST_STATUS,
    DBUS_ATTR_SMART_TEMPERATURE,
    DBUS_ATTR_SMART_UPDATED,
    DBUS_ATTR_STATE,
    DBUS_ATTR_SUBSYSTEM_NQN,
    DBUS_ATTR_UNALLOCATED_CAPACITY,
    DBUS_IFACE_NVME_CONTROLLER,
    DBUS_NAME_UDISKS2,
)
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected
from .const import UDISKS2_DEFAULT_OPTIONS


@dataclass(frozen=True, slots=True)
class SmartStatus:
    """Smart status information for NVMe devices.

    https://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.NVMe.Controller.html#gdbus-method-org-freedesktop-UDisks2-NVMe-Controller.SmartGetAttributes
    """

    available_spare: int
    spare_threshold: int
    percent_used: int
    total_data_read: int
    total_data_written: int
    controller_busy_minutes: int
    power_cycles: int
    unsafe_shutdowns: int
    media_errors: int
    number_error_log_entries: int
    temperature_sensors: list[int]
    warning_composite_temperature: int
    critical_composite_temperature: int
    warning_temperature_minutes: int
    critical_temperature_minutes: int

    @classmethod
    def from_smart_get_attributes_resp(cls, resp: dict[str, Any]):
        """Convert SmartGetAttributes response dictionary to instance."""
        return cls(
            available_spare=resp["avail_spare"],
            spare_threshold=resp["spare_thresh"],
            percent_used=resp["percent_used"],
            total_data_read=resp["total_data_read"],
            total_data_written=resp["total_data_written"],
            controller_busy_minutes=resp["ctrl_busy_time"],
            power_cycles=resp["power_cycles"],
            unsafe_shutdowns=resp["unsafe_shutdowns"],
            media_errors=resp["media_errors"],
            number_error_log_entries=resp["num_err_log_entries"],
            temperature_sensors=resp["temp_sensors"],
            warning_composite_temperature=resp["wctemp"],
            critical_composite_temperature=resp["cctemp"],
            warning_temperature_minutes=resp["warning_temp_time"],
            critical_temperature_minutes=resp["critical_temp_time"],
        )


class UDisks2NVMeController(DBusInterfaceProxy):
    """Handle D-Bus interface for NVMe Controller object.

    https://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.NVMe.Controller.html
    """

    name: str = DBUS_IFACE_NVME_CONTROLLER
    bus_name: str = DBUS_NAME_UDISKS2
    properties_interface: str = DBUS_IFACE_NVME_CONTROLLER

    def __init__(self, object_path: str) -> None:
        """Initialize object."""
        self._object_path = object_path
        super().__init__()

    @staticmethod
    async def new(object_path: str, bus: MessageBus) -> "UDisks2NVMeController":
        """Create and connect object."""
        obj = UDisks2NVMeController(object_path)
        await obj.connect(bus)
        return obj

    @property
    def object_path(self) -> str:
        """Object path for dbus object."""
        return self._object_path

    @property
    @dbus_property
    def state(self) -> str:
        """Return NVMe controller state."""
        return self.properties[DBUS_ATTR_STATE]

    @property
    @dbus_property
    def controller_id(self) -> int:
        """Return controller ID."""
        return self.properties[DBUS_ATTR_CONTROLLER_ID]

    @property
    @dbus_property
    def subsystem_nqn(self) -> str:
        """Return NVM Subsystem NVMe Qualified Name."""
        return cast(bytes, self.properties[DBUS_ATTR_SUBSYSTEM_NQN]).decode("utf-8")

    @property
    @dbus_property
    def fguid(self) -> str:
        """Return FRU GUID."""
        return self.properties[DBUS_ATTR_FGUID]

    @property
    @dbus_property
    def nvme_revision(self) -> str:
        """Return NVMe version information."""
        return self.properties[DBUS_ATTR_NVME_REVISION]

    @property
    @dbus_property
    def unallocated_capacity(self) -> int:
        """Return unallocated capacity."""
        return self.properties[DBUS_ATTR_UNALLOCATED_CAPACITY]

    @property
    @dbus_property
    def smart_updated(self) -> datetime | None:
        """Return last time smart information was updated (or None if it hasn't been).

        If this is None other smart properties are not meaningful.
        """
        if not (ts := self.properties[DBUS_ATTR_SMART_UPDATED]):
            return None
        return datetime.fromtimestamp(ts, UTC)

    @property
    @dbus_property
    def smart_critical_warning(self) -> list[str]:
        """Return critical warnings issued for current state of controller."""
        return self.properties[DBUS_ATTR_SMART_CRITICAL_WARNING]

    @property
    @dbus_property
    def smart_power_on_hours(self) -> int:
        """Return hours the disk has been powered on."""
        return self.properties[DBUS_ATTR_SMART_POWER_ON_HOURS]

    @property
    @dbus_property
    def smart_temperature(self) -> int:
        """Return current composite temperature of controller in Kelvin."""
        return self.properties[DBUS_ATTR_SMART_TEMPERATURE]

    @property
    @dbus_property
    def smart_selftest_status(self) -> str:
        """Return status of last sel-test."""
        return self.properties[DBUS_ATTR_SMART_SELFTEST_STATUS]

    @property
    @dbus_property
    def smart_selftest_percent_remaining(self) -> int:
        """Return percent remaining of self-test."""
        return self.properties[DBUS_ATTR_SMART_SELFTEST_PERCENT_REMAINING]

    @property
    @dbus_property
    def sanitize_status(self) -> str:
        """Return status of last sanitize operation."""
        return self.properties[DBUS_ATTR_SANITIZE_STATUS]

    @property
    @dbus_property
    def sanitize_percent_remaining(self) -> int:
        """Return percent remaining of sanitize operation."""
        return self.properties[DBUS_ATTR_SANITIZE_PERCENT_REMAINING]

    @dbus_connected
    async def smart_get_attributes(self) -> SmartStatus:
        """Return smart/health information of controller."""
        return SmartStatus.from_smart_get_attributes_resp(
            await self.connected_dbus.NVMe.Controller.call(
                "smart_get_attributes", UDISKS2_DEFAULT_OPTIONS
            )
        )
