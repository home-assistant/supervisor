"""Power control for host."""

from datetime import datetime
import logging

from awesomeversion import AwesomeVersion

from ..const import HostFeature
from ..coresys import CoreSysAttributes
from ..exceptions import (
    DBusInvalidArgsError,
    HostInvalidHostnameError,
    HostNotSupportedError,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

# First HAOS release whose hassos-supervisor.service has a stop timeout long
# enough for the SIGTERM handler to run the managed shutdown while the host is
# tearing down. On older releases Supervisor stops Core, apps and plugins
# in-process before requesting the reboot/power off instead.
HAOS_GRACEFUL_SHUTDOWN_MIN_VERSION = AwesomeVersion("18.0.dev20260527")


class SystemControl(CoreSysAttributes):
    """Handle host power controls."""

    def __init__(self, coresys):
        """Initialize host power handling."""
        self.coresys = coresys

    def _check_dbus(self, flag: HostFeature) -> None:
        """Check if systemd is connect or raise error."""
        if flag in (HostFeature.SHUTDOWN, HostFeature.REBOOT) and (
            self.sys_dbus.systemd.is_connected or self.sys_dbus.logind.is_connected
        ):
            return
        if flag == HostFeature.HOSTNAME and self.sys_dbus.hostname.is_connected:
            return
        if flag == HostFeature.TIMEDATE and self.sys_dbus.timedate.is_connected:
            return

        raise HostNotSupportedError(
            f"No {flag!s} D-Bus connection available", _LOGGER.error
        )

    def _os_coordinates_graceful_shutdown(self) -> bool:
        """Return True if the OS gives Supervisor time to shut down on teardown.

        Newer HAOS releases give hassos-supervisor.service a long stop timeout,
        so the SIGTERM handler can run the managed shutdown while the host is
        tearing down (see __main__.py). On older releases (or when not running
        HAOS) the timeout is too short, so Core, apps and plugins must be
        stopped in-process before the reboot/power off is requested.
        """
        return (
            self.coresys.os.available
            and self.sys_os.version is not None
            and self.sys_os.version >= HAOS_GRACEFUL_SHUTDOWN_MIN_VERSION
        )

    async def reboot(self) -> None:
        """Reboot host system."""
        self._check_dbus(HostFeature.REBOOT)

        use_logind = self.sys_dbus.logind.is_connected
        _LOGGER.info(
            "Initialize host reboot using %s", "logind" if use_logind else "systemd"
        )

        try:
            if not self._os_coordinates_graceful_shutdown():
                await self.sys_core.shutdown()
        finally:
            if use_logind:
                await self.sys_dbus.logind.reboot()
            else:
                await self.sys_dbus.systemd.reboot()

    async def shutdown(self) -> None:
        """Shutdown host system."""
        self._check_dbus(HostFeature.SHUTDOWN)

        use_logind = self.sys_dbus.logind.is_connected
        _LOGGER.info(
            "Initialize host power off %s", "logind" if use_logind else "systemd"
        )

        try:
            if not self._os_coordinates_graceful_shutdown():
                await self.sys_core.shutdown()
        finally:
            if use_logind:
                await self.sys_dbus.logind.power_off()
            else:
                await self.sys_dbus.systemd.power_off()

    async def set_hostname(self, hostname: str) -> None:
        """Set local a new Hostname."""
        self._check_dbus(HostFeature.HOSTNAME)

        _LOGGER.info("Set hostname %s", hostname)
        try:
            await self.sys_dbus.hostname.set_static_hostname(hostname)
        except DBusInvalidArgsError as err:
            raise HostInvalidHostnameError(hostname=hostname) from err

    async def set_datetime(self, new_time: datetime) -> None:
        """Update host clock with new (utc) datetime."""
        self._check_dbus(HostFeature.TIMEDATE)

        _LOGGER.info("Setting new host datetime: %s", new_time.isoformat())
        await self.sys_dbus.timedate.set_time(new_time)
        await self.sys_dbus.timedate.update()

    async def set_timezone(self, timezone: str) -> None:
        """Set timezone on host."""
        # /etc/localtime is not writable on OS older than 16.2
        if (
            self.coresys.os.available
            and self.coresys.os.version is not None
            and self.sys_os.version >= AwesomeVersion("16.2.dev20250814")
        ):
            self._check_dbus(HostFeature.TIMEDATE)
            _LOGGER.info("Setting host timezone: %s", timezone)
            await self.sys_dbus.timedate.set_timezone(timezone)
            await self.sys_dbus.timedate.update()
        else:
            _LOGGER.warning(
                "Skipping persistent timezone setting, OS %s is older than 16.2",
                self.sys_os.version,
            )
