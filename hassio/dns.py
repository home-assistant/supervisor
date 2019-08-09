"""Home Assistant control object."""
import asyncio
import logging
from pathlib import Path
from typing import List

from .utils.json import JsonConfig
from .validate import SCHEMA_DNS_CONFIG
from .const import (
    FILE_HASSIO_DNS,
    HASSIO_VERSION,
    ATTR_SERVERS,
    ATTR_VERSION,
    DNS_SERVERS,
)
from .coresys import CoreSys, CoreSysAttributes
from .docker.stats import DockerStats
from .docker.dns import DockerDNS
from .exceptions import (
    DockerAPIError,
    HostAppArmorError,
    SupervisorError,
    SupervisorUpdateError,
)

_LOGGER = logging.getLogger(__name__)


class CoreDNS(JsonConfig, CoreSysAttributes):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_DNS, SCHEMA_DNS_CONFIG)
        self.coresys: CoreSys = coresys
        self.instance: DockerDNS = DockerDNS(coresys)

    @property
    def servers(self) -> List[str]:
        """Return list of DNS servers."""
        return self._data[ATTR_SERVERS]

    @servers.setter
    def servers(self, value: List[str]) -> None:
        """Return list of DNS servers."""
        self._data[ATTR_SERVERS] = value

    @property
    def version(self) -> str:
        """Return current version of DNS."""
        return self._data[ATTR_VERSION]

    @version.setter
    def version(self, value: str) -> None:
        """Return current version of DNS."""
        self._data[ATTR_VERSION] = value

    async def load(self) -> None:
        """Load DNS setup."""
