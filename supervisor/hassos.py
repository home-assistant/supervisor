"""HassOS support on supervisor."""
import asyncio
import logging
from pathlib import Path
from typing import Awaitable, Optional

import aiohttp
from awesomeversion import AwesomeVersion, AwesomeVersionException
from cpe import CPE

from .coresys import CoreSys, CoreSysAttributes
from .dbus.rauc import RaucState
from .exceptions import DBusError, HassOSJobError, HassOSUpdateError
from .jobs.const import JobCondition, JobExecutionLimit
from .jobs.decorator import Job

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HassOS(CoreSysAttributes):
    """HassOS interface inside supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize HassOS handler."""
        self.coresys: CoreSys = coresys
        self._available: bool = False
        self._version: Optional[AwesomeVersion] = None
        self._board: Optional[str] = None

    @property
    def available(self) -> bool:
        """Return True, if HassOS on host."""
        return self._available

    @property
    def version(self) -> Optional[AwesomeVersion]:
        """Return version of HassOS."""
        return self._version

    @property
    def latest_version(self) -> Optional[AwesomeVersion]:
        """Return version of HassOS."""
        return self.sys_updater.version_hassos

    @property
    def need_update(self) -> bool:
        """Return true if a HassOS update is available."""
        try:
            return self.version < self.latest_version
        except (AwesomeVersionException, TypeError):
            return False

    @property
    def board(self) -> Optional[str]:
        """Return board name."""
        return self._board

    async def _download_raucb(self, version: AwesomeVersion) -> Path:
        """Download rauc bundle (OTA) from github."""
        raw_url = self.sys_updater.ota_url
        if raw_url is None:
            raise HassOSUpdateError("Don't have an URL for OTA updates!", _LOGGER.error)
        url = raw_url.format(version=str(version), board=self.board)

        _LOGGER.info("Fetch OTA update from %s", url)
        raucb = Path(self.sys_config.path_tmp, f"hassos-{version!s}.raucb")
        try:
            timeout = aiohttp.ClientTimeout(total=60 * 60, connect=180)
            async with self.sys_websession.get(url, timeout=timeout) as request:
                if request.status != 200:
                    raise HassOSUpdateError(
                        f"Error raise form OTA Webserver: {request.status}",
                        _LOGGER.error,
                    )

                # Download RAUCB file
                with raucb.open("wb") as ota_file:
                    while True:
                        chunk = await request.content.read(1_048_576)
                        if not chunk:
                            break
                        ota_file.write(chunk)

            _LOGGER.info("Completed download of OTA update file %s", raucb)
            return raucb

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            self.sys_supervisor.connectivity = False
            raise HassOSUpdateError(
                f"Can't fetch OTA update from {url}: {err!s}", _LOGGER.error
            ) from err

        except OSError as err:
            raise HassOSUpdateError(
                f"Can't write OTA file: {err!s}", _LOGGER.error
            ) from err

    async def load(self) -> None:
        """Load HassOS data."""
        try:
            if not self.sys_host.info.cpe:
                raise NotImplementedError()

            cpe = CPE(self.sys_host.info.cpe)
            os_name = cpe.get_product()[0]
            if os_name not in ("hassos", "haos"):
                raise NotImplementedError()
        except NotImplementedError:
            _LOGGER.info("No Home Assistant Operating System found")
            return
        else:
            self._available = True
            self.sys_host.supported_features.cache_clear()

        # Store meta data
        self._version = AwesomeVersion(cpe.get_version()[0])
        self._board = cpe.get_target_hardware()[0]

        await self.sys_dbus.rauc.update()

        _LOGGER.info(
            "Detect Home Assistant Operating System %s / BootSlot %s",
            self.version,
            self.sys_dbus.rauc.boot_slot,
        )

    @Job(
        conditions=[JobCondition.HAOS],
        on_condition=HassOSJobError,
    )
    async def config_sync(self) -> Awaitable[None]:
        """Trigger a host config reload from usb.

        Return a coroutine.
        """
        _LOGGER.info(
            "Synchronizing configuration from USB with Home Assistant Operating System."
        )
        await self.sys_host.services.restart("hassos-config.service")

    @Job(
        conditions=[JobCondition.HAOS, JobCondition.INTERNET_SYSTEM],
        limit=JobExecutionLimit.ONCE,
        on_condition=HassOSJobError,
    )
    async def update(self, version: Optional[AwesomeVersion] = None) -> None:
        """Update HassOS system."""
        version = version or self.latest_version

        # Check installed version
        if version == self.version:
            raise HassOSUpdateError(
                f"Version {version!s} is already installed", _LOGGER.warning
            )

        # Fetch files from internet
        int_ota = await self._download_raucb(version)
        ext_ota = Path(self.sys_config.path_extern_tmp, int_ota.name)

        try:
            await self.sys_dbus.rauc.install(ext_ota)
            completed = await self.sys_dbus.rauc.signal_completed()

        except DBusError as err:
            raise HassOSUpdateError("Rauc communication error", _LOGGER.error) from err

        finally:
            int_ota.unlink()

        # Update success
        if 0 in completed:
            _LOGGER.info(
                "Install of Home Assistant Operating System %s success", version
            )
            self.sys_create_task(self.sys_host.control.reboot())
            return

        # Update failed
        await self.sys_dbus.rauc.update()
        _LOGGER.error(
            "Home Assistant Operating System update failed with: %s",
            self.sys_dbus.rauc.last_error,
        )
        raise HassOSUpdateError()

    @Job(conditions=[JobCondition.HAOS])
    async def mark_healthy(self) -> None:
        """Set booted partition as good for rauc."""
        try:
            response = await self.sys_dbus.rauc.mark(RaucState.GOOD, "booted")
        except DBusError:
            _LOGGER.error("Can't mark booted partition as healty!")
        else:
            _LOGGER.info("Rauc: %s - %s", self.sys_dbus.rauc.boot_slot, response[1])
