"""Mock of OS Agent Boards Raspberry Pi Firmware dbus service."""

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method

BUS_NAME = "io.hass.os"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return RPiFirmware()


class RPiFirmware(DBusServiceMock):
    """Raspberry Pi firmware mock.

    gdbus introspect --system --dest io.hass.os \
        --object-path /io/hass/os/Boards/RaspberryPi/Firmware
    """

    object_path = "/io/hass/os/Boards/RaspberryPi/Firmware"
    interface = "io.hass.os.Boards.RaspberryPi.Firmware"

    update_called: bool = False
    _current_version: str = "1618412973"
    _latest_version: str = "1700000000"
    _update_available: bool = True
    _update_blocked: bool = False
    _update_pending: bool = False
    _blocked_reason: str = ""

    def set_state(
        self,
        *,
        current_version: str | None = None,
        latest_version: str | None = None,
        update_available: bool | None = None,
        update_blocked: bool | None = None,
        update_pending: bool | None = None,
        blocked_reason: str | None = None,
    ) -> None:
        """Update mock state and emit PropertiesChanged for changed values."""
        changed: dict[str, object] = {}
        if current_version is not None and current_version != self._current_version:
            self._current_version = current_version
            changed["CurrentVersion"] = current_version
        if latest_version is not None and latest_version != self._latest_version:
            self._latest_version = latest_version
            changed["LatestVersion"] = latest_version
        if update_available is not None and update_available != self._update_available:
            self._update_available = update_available
            changed["UpdateAvailable"] = update_available
        if update_blocked is not None and update_blocked != self._update_blocked:
            self._update_blocked = update_blocked
            changed["UpdateBlocked"] = update_blocked
        if update_pending is not None and update_pending != self._update_pending:
            self._update_pending = update_pending
            changed["UpdatePending"] = update_pending
        if blocked_reason is not None and blocked_reason != self._blocked_reason:
            self._blocked_reason = blocked_reason
            changed["BlockedReason"] = blocked_reason
        if changed:
            self.emit_properties_changed(changed)

    @dbus_property(access=PropertyAccess.READ)
    def CurrentVersion(self) -> "s":
        """Get current installed firmware version."""
        return self._current_version

    @dbus_property(access=PropertyAccess.READ)
    def LatestVersion(self) -> "s":
        """Get latest available firmware version."""
        return self._latest_version

    @dbus_property(access=PropertyAccess.READ)
    def UpdateAvailable(self) -> "b":
        """Return True if an update is available."""
        return self._update_available

    @dbus_property(access=PropertyAccess.READ)
    def UpdateBlocked(self) -> "b":
        """Return True if updates are blocked."""
        return self._update_blocked

    @dbus_property(access=PropertyAccess.READ)
    def UpdatePending(self) -> "b":
        """Return True if an update was applied and a reboot is needed."""
        return self._update_pending

    @dbus_property(access=PropertyAccess.READ)
    def BlockedReason(self) -> "s":
        """Get the blocked-reason (empty when not blocked)."""
        return self._blocked_reason

    @dbus_method()
    def Update(self) -> None:
        """Apply firmware (bootloader EEPROM and VL805 where present) update."""
        self.update_called = True
