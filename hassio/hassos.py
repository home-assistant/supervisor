"""HassOS support on supervisor."""
import logging

from cpe import CPE

from .coresys import CoreSysAttributes
from .exceptions import HassioNotSupportedError

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
            raise HassioNotSupportedError()

    async def load(self):
        """Load HassOS data."""
        try:
            assert self.sys_host.info.cpe is not None
            cpe = CPE(self.sys_host.info.cpe)
            assert cpe.get_product()[0] == 'hassos'
        except (NotImplementedError, IndexError, AssertionError):
            _LOGGER.info("Can't detect HassOS")
            return

        # Store meta data
        self._available = True
        self._version = cpe.get_version()[0]
        self._board = cpe.get_target_hardware()[0]

        _LOGGER.info("Detect HassOS %s on host system", self.version)

    def config_sync(self):
        """Trigger a host config reload from usb."""
        self._check_host()

        _LOGGER.info("Sync config from USB on HassOS.")
        return self.sys_host.services.restart('hassos-config.service')
