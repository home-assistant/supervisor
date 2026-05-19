"""Power control for host."""

import asyncio
from datetime import datetime
import logging

from awesomeversion import AwesomeVersion

from ..const import HostFeature
from ..coresys import CoreSysAttributes
from ..dbus.const import StartUnitMode, UnitActiveState
from ..exceptions import (
    DBusInvalidArgsError,
    DBusSystemdNoSuchUnit,
    HassioError,
    HostInvalidHostnameError,
    HostNotSupportedError,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

HAOS_PRE_SHUTDOWN_TARGET = "haos-pre-shutdown.target"
HAOS_PRE_SHUTDOWN_TIMEOUT = 10


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

    async def _enter_haos_pre_shutdown(self) -> None:
        """Enter the HAOS pre-shutdown systemd phase if available."""
        if not self.sys_dbus.systemd.is_connected:
            return

        try:
            _LOGGER.info("Entering Home Assistant OS pre-shutdown phase")
            await self.sys_dbus.systemd.start_unit(
                HAOS_PRE_SHUTDOWN_TARGET, StartUnitMode.REPLACE
            )
            unit = await self.sys_dbus.systemd.get_unit(HAOS_PRE_SHUTDOWN_TARGET)
            async with asyncio.timeout(HAOS_PRE_SHUTDOWN_TIMEOUT):
                await unit.wait_for_active_state({UnitActiveState.ACTIVE})
        except DBusSystemdNoSuchUnit:
            _LOGGER.debug("Home Assistant OS pre-shutdown target is not available")
        except TimeoutError:
            _LOGGER.warning("Timed out entering Home Assistant OS pre-shutdown phase")
        except HassioError as err:
            _LOGGER.warning(
                "Could not enter Home Assistant OS pre-shutdown phase: %s", err
            )

    async def reboot(self) -> None:
        """Reboot host system."""
        self._check_dbus(HostFeature.REBOOT)

        use_logind = self.sys_dbus.logind.is_connected
        _LOGGER.info(
            "Initialize host reboot using %s", "logind" if use_logind else "systemd"
        )

        # Stop Home Assistant Core, add-ons and plugins before requesting the
        # reboot. Doing it here (rather than relying only on the SIGTERM
        # handler during host shutdown) keeps UI-triggered reboots fully
        # graceful on every OS version, including ones whose systemd units
        # give Supervisor only a short stop timeout.
        try:
            await self._enter_haos_pre_shutdown()
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

        # Stop Home Assistant Core, add-ons and plugins before requesting the
        # power off. Doing it here (rather than relying only on the SIGTERM
        # handler during host shutdown) keeps UI-triggered shutdowns fully
        # graceful on every OS version, including ones whose systemd units
        # give Supervisor only a short stop timeout.
        try:
            await self._enter_haos_pre_shutdown()
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
            # pylint: disable=fixme
            # TODO: we can change this to a warning once 16.2 is out
            _LOGGER.info(
                "Skipping persistent timezone setting, OS %s < 16.2",
                self.sys_os.version,
            )
