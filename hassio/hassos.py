"""HassOS support on supervisor."""
import logging

from cpe import CPE

from .coresys import CoreSysAttributes
from .exceptions import HassioNotSupportedError, HostServiceError

_LOGGER = logging.getLogger(__name__)


class HassOS(CoreSysAttributes):
    """HassOS interface inside HassIO."""

    def __init__(self, coresys):
        """Initialize HassOS handler."""
        self._cpe = None

    @property
    def availabe(self):
        """Return True, if HassOS on host."""
        return self._cpe is not None

    @property
    def version(self):
        """Return version of HassOS."""
        if not self._cpe:
            return None
        return self._cpe.get_version()[0]

    @property
    def board(self):
        """Return board name."""
        if not self._cpe:
            return None
        return self._cpe.get_other()[0]

    def _check_host(self):
        """Check if HassOS is availabe."""
        if not self.availabe:
            _LOGGER.error("No HassOS availabe")
            raise HassioNotSupportedError()

    async def load(self):
        """Load HassOS data."""
        try:
            self._cpe = CPE(self.sys_host.info.cpe)
            assert self._cpe.get_product()[0] == 'hassos'
        except (NotImplementedError, AttributeError, AssertionError):
            _LOGGER.info("Can't detect HassOS")
            return

    def config_sync(self):
        """Trigger a host config reload from usb."""
        self._check_host()
        return self.sys_host.services.restart('hassos-config.service')
