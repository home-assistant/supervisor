"""Mock of timedate dbus service."""

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.timedate1"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return TimeDate()


class TimeDate(DBusServiceMock):
    """TimeDate mock.

    gdbus introspect --system --dest org.freedesktop.timedate1 --object-path /org/freedesktop/timedate1
    """

    object_path = "/org/freedesktop/timedate1"
    interface = "org.freedesktop.timedate1"

    @dbus_property(access=PropertyAccess.READ)
    def Timezone(self) -> "s":
        """Get Timezone."""
        return "Etc/UTC"

    @dbus_property(access=PropertyAccess.READ)
    def LocalRTC(self) -> "b":
        """Get LocalRTC."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def CanNTP(self) -> "b":
        """Get CanNTP."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def NTP(self) -> "b":
        """Get NTP."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def NTPSynchronized(self) -> "b":
        """Get NTPSynchronized."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def TimeUSec(self) -> "t":
        """Get TimeUSec."""
        return 1621413414405718

    @dbus_property(access=PropertyAccess.READ)
    def RTCTimeUSec(self) -> "t":
        """Get RTCTimeUSec."""
        return 1621413415000000

    @dbus_method()
    def SetTime(self, usec_utc: "x", relative: "b", interactive: "b") -> None:
        """Set time."""

    @dbus_method()
    def SetTimezone(self, timezone: "s", interactive: "b") -> None:
        """Set timezone."""
        self.emit_properties_changed({"Timezone": timezone})

    @dbus_method()
    def SetLocalRTC(self, local_rtc: "b", fix_system: "b", interactive: "b") -> None:
        """Set local RTC."""
        self.emit_properties_changed({"LocalRTC": local_rtc})

    @dbus_method()
    def SetNTP(self, use_ntp: "b", interactive: "b") -> None:
        """Set NTP."""
        self.emit_properties_changed({"NTP": use_ntp})

    @dbus_method()
    def ListTimezones(self) -> "as":
        """List timezones."""
        return [
            "Africa/Abidjan",
            "America/New_York",
            "Antarctica/Casey",
            "Asia/Hong_Kong",
            "Atlantic/Azores",
            "Australia/Sydney",
            "Europe/Amsterdam",
            "Indian/Chagos",
            "Pacific/Apia",
            "UTC",
        ]
