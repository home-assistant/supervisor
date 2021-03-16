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
from .exceptions import DBusError, HassOSNotSupportedError, HassOSUpdateError
from .utils import process_lock

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HassOS(CoreSysAttributes):
    """HassOS interface inside supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize HassOS handler."""
        self.coresys: CoreSys = coresys
        self.lock: asyncio.Lock = asyncio.Lock()
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

    def _check_host(self) -> None:
        """Check if HassOS is available."""
        if not self.available:
            _LOGGER.error("No Home Assistant Operating System available")
            raise HassOSNotSupportedError()

    async def _download_raucb(self, version: AwesomeVersion) -> Path:
        """Download rauc bundle (OTA) from github."""
        raw_url = self.sys_updater.ota_url
        if raw_url is None:
            _LOGGER.error("Don't have an URL for OTA updates!")
            raise HassOSNotSupportedError()
        url = raw_url.format(version=str(version), board=self.board)

        _LOGGER.info("Fetch OTA update from %s", url)
        raucb = Path(self.sys_config.path_tmp, f"hassos-{version!s}.raucb")
        try:
            timeout = aiohttp.ClientTimeout(total=60 * 60, connect=180)
            async with self.sys_websession.get(url, timeout=timeout) as request:
                if request.status != 200:
                    raise HassOSUpdateError()

                # Download RAUCB file
                with raucb.open("wb") as ota_file:
                    while True:
                        chunk = await request.content.read(1_048_576)
                        if not chunk:
                            break
                        ota_file.write(chunk)

            _LOGGER.info("OTA update is downloaded on %s", raucb)
            return raucb

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            self.sys_supervisor.connectivity = False
            _LOGGER.warning("Can't fetch versions from %s: %s", url, err)

        except OSError as err:
            _LOGGER.error("Can't write OTA file: %s", err)

        raise HassOSUpdateError()

    async def load(self) -> None:
        """Load HassOS data."""
        try:
            if not self.sys_host.info.cpe:
                raise NotImplementedError()

            cpe = CPE(self.sys_host.info.cpe)
            os_name = cpe.get_product()[0]
            if os_name != "hassos" and os_name != "haos":
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
            "Detect HassOS %s / BootSlot %s", self.version, self.sys_dbus.rauc.boot_slot
        )

    def config_sync(self) -> Awaitable[None]:
        """Trigger a host config reload from usb.

        Return a coroutine.
        """
        self._check_host()

        _LOGGER.info(
            "Synchronizing configuration from USB with Home Assistant Operating System."
        )
        return self.sys_host.services.restart("hassos-config.service")

    @process_lock
    async def update(self, version: Optional[AwesomeVersion] = None) -> None:
        """Update HassOS system."""
        version = version or self.latest_version

        # Check installed version
        self._check_host()
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
            _LOGGER.error("Rauc communication error")
            raise HassOSUpdateError() from err

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

    async def mark_healthy(self) -> None:
        """Set booted partition as good for rauc."""
        try:
            response = await self.sys_dbus.rauc.mark(RaucState.GOOD, "booted")
        except DBusError:
            _LOGGER.error("Can't mark booted partition as healty!")
        else:
            _LOGGER.info("Rauc: %s - %s", self.sys_dbus.rauc.boot_slot, response[1])
