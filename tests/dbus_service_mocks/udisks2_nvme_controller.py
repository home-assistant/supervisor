"""Mock of UDisks2 Drive service."""

from dbus_fast import Variant
from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.UDisks2"
DEFAULT_OBJECT_PATH = (
    "/org/freedesktop/UDisks2/drives/Samsung_SSD_970_EVO_Plus_2TB_S40123456789ABC"
)


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return NVMeController(object_path if object_path else DEFAULT_OBJECT_PATH)


class NVMeController(DBusServiceMock):
    """NVMe Controller mock.

    gdbus introspect --system --dest org.freedesktop.UDisks2 --object-path /org/freedesktop/UDisks2/drives/id
    """

    interface = "org.freedesktop.UDisks2.NVMe.Controller"

    def __init__(self, object_path: str):
        """Initialize object."""
        super().__init__()
        self.object_path = object_path
        self.smart_get_attributes_response = {
            "avail_spare": Variant("y", 0x64),
            "spare_thresh": Variant("y", 0x0A),
            "percent_used": Variant("y", 0x01),
            "total_data_read": Variant("t", 22890461184000),
            "total_data_written": Variant("t", 27723431936000),
            "ctrl_busy_time": Variant("t", 2682),
            "power_cycles": Variant("t", 652),
            "unsafe_shutdowns": Variant("t", 107),
            "media_errors": Variant("t", 0),
            "num_err_log_entries": Variant("t", 1069),
            "temp_sensors": Variant("aq", [310, 305, 0, 0, 0, 0, 0, 0]),
            "wctemp": Variant("q", 358),
            "cctemp": Variant("q", 358),
            "warning_temp_time": Variant("i", 0),
            "critical_temp_time": Variant("i", 0),
        }

    @dbus_property(access=PropertyAccess.READ)
    def State(self) -> "s":
        """Get State."""
        return "live"

    @dbus_property(access=PropertyAccess.READ)
    def ControllerID(self) -> "q":
        """Get ControllerID."""
        return 4

    @dbus_property(access=PropertyAccess.READ)
    def SubsystemNQN(self) -> "ay":
        """Get SubsystemNQN."""
        return b"nqn.2014.08.org.nvmexpress:144d144dS4J4NM0RB05961P     Samsung SSD 970 EVO Plus 2TB"

    @dbus_property(access=PropertyAccess.READ)
    def FGUID(self) -> "s":
        """Get FGUID."""
        return ""

    @dbus_property(access=PropertyAccess.READ)
    def NVMeRevision(self) -> "s":
        """Get NVMeRevision."""
        return "1.3"

    @dbus_property(access=PropertyAccess.READ)
    def UnallocatedCapacity(self) -> "t":
        """Get UnallocatedCapacity."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def SmartUpdated(self) -> "t":
        """Get SmartUpdated."""
        return 1753906112

    @dbus_property(access=PropertyAccess.READ)
    def SmartCriticalWarning(self) -> "as":
        """Get SmartCriticalWarning."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def SmartPowerOnHours(self) -> "t":
        """Get SmartPowerOnHours."""
        return 3208

    @dbus_property(access=PropertyAccess.READ)
    def SmartTemperature(self) -> "q":
        """Get SmartTemperature."""
        return 311

    @dbus_property(access=PropertyAccess.READ)
    def SmartSelftestStatus(self) -> "s":
        """Get SmartSelftestStatus."""
        return "success"

    @dbus_property(access=PropertyAccess.READ)
    def SmartSelftestPercentRemaining(self) -> "i":
        """Get SmartSelftestPercentRemaining."""
        return -1

    @dbus_property(access=PropertyAccess.READ)
    def SanitizeStatus(self) -> "s":
        """Get SanitizeStatus."""
        return ""

    @dbus_property(access=PropertyAccess.READ)
    def SanitizePercentRemaining(self) -> "i":
        """Get SanitizePercentRemaining."""
        return -1

    @dbus_method()
    def SmartUpdate(self, options: "a{sv}") -> None:
        """Do SmartUpdate."""

    @dbus_method()
    def SmartGetAttributes(self, options: "a{sv}") -> "a{sv}":
        """Do SmartGetAttributes."""
        return self.smart_get_attributes_response

    @dbus_method()
    def SmartSelftestStart(self, type_: "s", options: "a{sv}") -> None:
        """Do SmartSelftestStart."""

    @dbus_method()
    def SmartSelftestAbort(self, options: "a{sv}") -> None:
        """Do SmartSelftestAbort."""

    @dbus_method()
    def SanitizeStart(self, action: "s", options: "a{sv}") -> None:
        """Do SanitizeStart."""
