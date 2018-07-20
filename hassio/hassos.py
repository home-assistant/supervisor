"""HassOS support on supervisor."""
import logging
from pathlib import Path

import aiohttp
from cpe import CPE

from .coresys import CoreSysAttributes
from .const import URL_HASSOS_OTA
from .docker.hassos_cli import DockerHassOSCli
from .exceptions import HassOSNotSupportedError, HassOSUpdateError, DBusError

_LOGGER = logging.getLogger(__name__)


class HassOS(CoreSysAttributes):
    """HassOS interface inside HassIO."""

    def __init__(self, coresys):
        """Initialize HassOS handler."""
        self.coresys = coresys
        self.instance = DockerHassOSCli(coresys)
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
    def version_cli(self):
        """Return version of HassOS cli."""
        return self.instance.version

    @property
    def version_latest(self):
        """Return version of HassOS."""
        return self.sys_updater.version_hassos

    @property
    def version_cli_latest(self):
        """Return version of HassOS."""
        return self.sys_updater.version_hassos_cli

    @property
    def need_update(self):
        """Return true if a HassOS update is available."""
        return self.version != self.version_latest

    @property
    def need_cli_update(self):
        """Return true if a HassOS cli update is available."""
        return self.version_cli != self.version_cli_latest

    @property
    def board(self):
        """Return board name."""
        return self._board

    def _check_host(self):
        """Check if HassOS is availabe."""
        if not self.available:
            _LOGGER.error("No HassOS availabe")
            raise HassOSNotSupportedError()

    async def _download_raucb(self, version):
        """Download rauc bundle (OTA) from github."""
        url = URL_HASSOS_OTA.format(version=version, board=self.board)
        raucb = Path(self.sys_config.path_tmp, f"hassos-{version}.raucb")

        try:
            _LOGGER.info("Fetch OTA update from %s", url)
            async with self.sys_websession.get(url) as request:
                if request.status != 200:
                    raise HassOSUpdateError()

                # Download RAUCB file
                with raucb.open('wb') as ota_file:
                    while True:
                        chunk = await request.content.read(1048576)
                        if not chunk:
                            break
                        ota_file.write(chunk)

            _LOGGER.info("OTA update is downloaded on %s", raucb)
            return raucb

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.warning("Can't fetch versions from %s: %s", url, err)

        except OSError as err:
            _LOGGER.error("Can't write ota file: %s", err)

        raise HassOSUpdateError()

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
            _LOGGER.debug("Found no HassOS")
            return

        # Store meta data
        self._available = True
        self._version = cpe.get_version()[0]
        self._board = cpe.get_target_hardware()[0]

        _LOGGER.info("Detect HassOS %s on host system", self.version)
        await self.instance.attach()

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
        rauc_status = await self.sys_dbus.get_properties()
        _LOGGER.error(
            "HassOS update fails with: %s", rauc_status.get('LastError'))
        raise HassOSUpdateError()

    async def update_cli(self, version=None):
        """Update local HassOS cli."""
        version = version or self.version_cli_latest

        if version == self.version_cli:
            _LOGGER.warning("Version %s is already installed for CLI", version)
            raise HassOSUpdateError()

        if await self.instance.update(version):
            return

        _LOGGER.error("HassOS CLI update fails.")
        raise HassOSUpdateError()
