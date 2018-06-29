"""HassOS support on supervisor."""
import logging
from pathlib import Path

import aiohttp
from cpe import CPE

from .coresys import CoreSysAttributes
from .const import URL_HASSOS_OTA
from .exceptions import HassOSNotSupportedError, HassOSUpdateError

_LOGGER = logging.getLogger(__name__)


class HassOS(CoreSysAttributes):
    """HassOS interface inside HassIO."""

    def __init__(self, coresys):
        """Initialize HassOS handler."""
        self.coresys = coresys
        self._available = False
        self._version = None
        self._board = None

    @property
    def available(self):
        """Return True, if HassOS on host."""
        return self._available

    @property
    def version(self):
        """Return version of HassOS."""
        return self._version

    @property
    def version_latest(self):
        """Return version of HassOS."""
        return self.sys_updater.version_hassos

    @property
    def board(self):
        """Return board name."""
        return self._board

    def _check_host(self):
        """Check if HassOS is availabe."""
        if not self.available:
            _LOGGER.error("No HassOS availabe")
            raise HassOSNotSupportedError()

    async def _download_ota(self, version):
        """Download rauc bundle from github."""
        url = URL_HASSOS_OTA(version=version, board=self.board)
        raucb = Path(self.sys_config.path_tmp, f"hassos-{version}.raucb")
        
        try:
            _LOGGER.info("Fetch OTA update from %s", url)
            async with self.sys_websession.get(url) as request:
                with raucb('wb') ota_file:
                    while True:
                        chunk = await request.content.read(1048576)
                        if not chunk:
                            break
                        ota_file.write(chunk)
                        
            _LOGGER.info("OTA update is downloaded on %s", raucb)
            return raucb

        except aiohttp.ClientError as err:
            _LOGGER.warning("Can't fetch versions from %s: %s", url, err)
            
        except OSError as err:
            _LOGGER.error("Can't write ota file: %s", err)
            
        raise HassOSUpdateError
            
    async def load(self):
        """Load HassOS data."""
        try:
            # Check needed host functions
            assert self.sys_dbus.rauc.is_connected
            assert self.sys_dbus.systemd.is_connected
            assert self.sys_dbus.hostname.is_connected
            
            assert self.sys_host.info.cpe is not None
            cpe = CPE(self.sys_host.info.cpe)
            assert cpe.get_product()[0] == 'hassos'
        except (AssertionError, NotImplementedError):
            _LOGGER.debug("Ignore HassOS")
            return

        # Store meta data
        self._available = True
        self._version = cpe.get_version()[0]
        self._board = cpe.get_target_hardware()[0]

        _LOGGER.info("Detect HassOS %s on host system", self.version)

    def config_sync(self):
        """Trigger a host config reload from usb.

        Return a coroutine.
        """
        self._check_host()

        _LOGGER.info("Sync config from USB on HassOS.")
        return self.sys_host.services.restart('hassos-config.service')

    async def update(self, version=None):
        """Update HassOS system."""
        version = version or self.version_latest

        self._check_host()
