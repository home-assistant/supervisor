"""Interface to Systemd over D-Bus."""

from functools import wraps
import logging

from dbus_fast import Variant
from dbus_fast.aio.message_bus import MessageBus

from ..exceptions import (
    DBusError,
    DBusFatalError,
    DBusInterfaceError,
    DBusSystemdNoSuchUnit,
)
from .const import (
    DBUS_ATTR_FINISH_TIMESTAMP,
    DBUS_ATTR_FIRMWARE_TIMESTAMP_MONOTONIC,
    DBUS_ATTR_KERNEL_TIMESTAMP_MONOTONIC,
    DBUS_ATTR_LOADER_TIMESTAMP_MONOTONIC,
    DBUS_ATTR_USERSPACE_TIMESTAMP_MONOTONIC,
    DBUS_ERR_SYSTEMD_NO_SUCH_UNIT,
    DBUS_IFACE_SYSTEMD_MANAGER,
    DBUS_NAME_SYSTEMD,
    DBUS_OBJECT_SYSTEMD,
    StartUnitMode,
    StopUnitMode,
    UnitActiveState,
)
from .interface import DBusInterface, DBusInterfaceProxy, dbus_property
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


def systemd_errors(func):
    """Wrap systemd dbus methods to handle its specific error types."""

    @wraps(func)
    async def wrapper(*args, **kwds):
        try:
            return await func(*args, **kwds)
        except DBusFatalError as err:
            if err.type == DBUS_ERR_SYSTEMD_NO_SUCH_UNIT:
                # pylint: disable=raise-missing-from
                raise DBusSystemdNoSuchUnit(str(err))
                # pylint: enable=raise-missing-from
            raise err

    return wrapper


class SystemdUnit(DBusInterface):
    """Systemd service unit."""

    name: str = DBUS_NAME_SYSTEMD
    bus_name: str = DBUS_NAME_SYSTEMD

    def __init__(self, object_path: str) -> None:
        """Initialize object."""
        super().__init__()
        self.object_path = object_path

    @dbus_connected
    async def get_active_state(self) -> UnitActiveState:
        """Get active state of the unit."""
        return await self.dbus.Unit.get_active_state()


class Systemd(DBusInterfaceProxy):
    """Systemd function handler.

    https://www.freedesktop.org/software/systemd/man/org.freedesktop.systemd1.html
    """

    name: str = DBUS_NAME_SYSTEMD
    bus_name: str = DBUS_NAME_SYSTEMD
    object_path: str = DBUS_OBJECT_SYSTEMD
    # NFailedUnits is the only property that emits a change signal and we don't use it
    sync_properties: bool = False
    properties_interface: str = DBUS_IFACE_SYSTEMD_MANAGER

    async def connect(self, bus: MessageBus):
        """Connect to D-Bus."""
        _LOGGER.info("Load dbus interface %s", self.name)
        try:
            await super().connect(bus)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No systemd support on the host. Host control has been disabled."
            )

    @property
    @dbus_property
    def startup_time(self) -> float:
        """Return startup time in seconds."""
        return (
            float(self.properties[DBUS_ATTR_FIRMWARE_TIMESTAMP_MONOTONIC])
            + float(self.properties[DBUS_ATTR_LOADER_TIMESTAMP_MONOTONIC])
            + float(self.properties[DBUS_ATTR_KERNEL_TIMESTAMP_MONOTONIC])
            + float(self.properties[DBUS_ATTR_USERSPACE_TIMESTAMP_MONOTONIC])
        ) / 1e6

    @property
    @dbus_property
    def boot_timestamp(self) -> int:
        """Return the boot timestamp."""
        return self.properties[DBUS_ATTR_FINISH_TIMESTAMP]

    @dbus_connected
    async def reboot(self) -> None:
        """Reboot host computer."""
        await self.dbus.Manager.call_reboot()

    @dbus_connected
    async def power_off(self) -> None:
        """Power off host computer."""
        await self.dbus.Manager.call_power_off()

    @dbus_connected
    @systemd_errors
    async def start_unit(self, unit: str, mode: StartUnitMode) -> str:
        """Start a systemd service unit. Returns object path of job."""
        return await self.dbus.Manager.call_start_unit(unit, mode)

    @dbus_connected
    @systemd_errors
    async def stop_unit(self, unit: str, mode: StopUnitMode) -> str:
        """Stop a systemd service unit. Returns object path of job."""
        return await self.dbus.Manager.call_stop_unit(unit, mode)

    @dbus_connected
    @systemd_errors
    async def reload_unit(self, unit: str, mode: StartUnitMode) -> str:
        """Reload a systemd service unit. Returns object path of job."""
        return await self.dbus.Manager.call_reload_or_restart_unit(unit, mode)

    @dbus_connected
    @systemd_errors
    async def restart_unit(self, unit: str, mode: StartUnitMode) -> str:
        """Restart a systemd service unit. Returns object path of job."""
        return await self.dbus.Manager.call_restart_unit(unit, mode)

    @dbus_connected
    async def list_units(
        self,
    ) -> list[tuple[str, str, str, str, str, str, str, int, str, str]]:
        """Return a list of available systemd services."""
        return await self.dbus.Manager.call_list_units()

    @dbus_connected
    async def start_transient_unit(
        self, unit: str, mode: StartUnitMode, properties: list[tuple[str, Variant]]
    ) -> str:
        """Start a transient unit which is released when stopped or on reboot. Returns object path of job."""
        return await self.dbus.Manager.call_start_transient_unit(
            unit, mode, properties, []
        )

    @dbus_connected
    @systemd_errors
    async def reset_failed_unit(self, unit: str) -> None:
        """Reset the failed state of a unit."""
        await self.dbus.Manager.call_reset_failed_unit(unit)

    @dbus_connected
    @systemd_errors
    async def get_unit(self, unit: str) -> SystemdUnit:
        """Return systemd unit for unit name."""
        obj_path = await self.dbus.Manager.call_get_unit(unit)
        unit = SystemdUnit(obj_path)
        await unit.connect(self.dbus.bus)
        return unit
