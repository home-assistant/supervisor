"""HassOS support on supervisor."""
import asyncio
import logging
from pathlib import Path
from typing import Awaitable, Optional

import aiohttp
from cpe import CPE

from .const import URL_HASSOS_OTA
from .coresys import CoreSysAttributes, CoreSys
from .exceptions import (
    DBusError,
    HassOSNotSupportedError,
    HassOSUpdateError,
)
from .dbus.rauc import RaucState

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HassOS(CoreSysAttributes):
    """HassOS interface inside supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize HassOS handler."""
        self.coresys: CoreSys = coresys
        self._available: bool = False
        self._version: Optional[str] = None
        self._board: Optional[str] = None

    @property
    def available(self) -> bool:
        """Return True, if HassOS on host."""
        return self._available

    @property
    def version(self) -> Optional[str]:
        """Return version of HassOS."""
        return self._version

    @property
    def version_latest(self) -> str:
        """Return version of HassOS."""
        return self.sys_updater.version_hassos

    @property
    def need_update(self) -> bool:
        """Return true if a HassOS update is available."""
        return self.version != self.version_latest

    @property
    def board(self) -> Optional[str]:
        """Return board name."""
        return self._board

    def _check_host(self) -> None:
        """Check if HassOS is available."""
        if not self.available:
            _LOGGER.error("No HassOS available")
            raise HassOSNotSupportedError()

    async def _download_raucb(self, version: str) -> None:
        """Download rauc bundle (OTA) from github."""
        url = URL_HASSOS_OTA.format(version=version, board=self.board)
        raucb = Path(self.sys_config.path_tmp, f"hassos-{version}.raucb")

        _LOGGER.info("Fetch OTA update from %s", url)
        try:
            timeout = aiohttp.ClientTimeout(total=600)
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
            if cpe.get_product()[0] != "hassos":
                raise NotImplementedError()
        except NotImplementedError:
            _LOGGER.debug("Found no HassOS")
            return
        else:
            self._available = True

        # Store meta data
        self._version = cpe.get_version()[0]
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

        _LOGGER.info("Syncing configuration from USB with HassOS.")
        return self.sys_host.services.restart("hassos-config.service")

    async def update(self, version: Optional[str] = None) -> None:
        """Update HassOS system."""
        version = version or self.version_latest

        # Check installed version
        self._check_host()
        if version == self.version:
            _LOGGER.warning("Version %s is already installed", version)
            raise HassOSUpdateError()

        # Fetch files from internet
        int_ota = await self._download_raucb(version)
        ext_ota = Path(self.sys_config.path_extern_tmp, int_ota.name)

        try:
            await self.sys_dbus.rauc.install(ext_ota)
            completed = await self.sys_dbus.rauc.signal_completed()

        except DBusError:
            _LOGGER.error("Rauc communication error")
            raise HassOSUpdateError() from None

        finally:
            int_ota.unlink()

        # Update success
        if 0 in completed:
            _LOGGER.info("Install HassOS %s success", version)
            self.sys_create_task(self.sys_host.control.reboot())
            return

        # Update fails
        await self.sys_dbus.rauc.update()
        _LOGGER.error("HassOS update fails with: %s", self.sys_dbus.rauc.last_error)
        raise HassOSUpdateError()

    async def mark_healthy(self):
        """Set booted partition as good for rauc."""
        try:
            response = await self.sys_dbus.rauc.mark(RaucState.GOOD, "booted")
        except DBusError:
            _LOGGER.error("Can't mark booted partition as healty!")
        else:
            _LOGGER.info("Rauc: %s - %s", self.sys_dbus.rauc.boot_slot, response[1])
