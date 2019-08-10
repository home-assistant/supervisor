"""Home Assistant control object."""
import asyncio
from contextlib import suppress
import logging
from pathlib import Path
from typing import Awaitable, List, Optional

from .const import (
    ATTR_SERVERS,
    ATTR_VERSION,
    DNS_SERVERS,
    FILE_HASSIO_DNS,
    HASSIO_VERSION,
)
from .coresys import CoreSys, CoreSysAttributes
from .docker.dns import DockerDNS
from .docker.stats import DockerStats
from .exceptions import CoreDNSError, CoreDNSUpdateError, DockerAPIError
from .misc.forwarder import DNSForward
from .utils.json import JsonConfig
from .validate import SCHEMA_DNS_CONFIG

_LOGGER = logging.getLogger(__name__)


class CoreDNS(JsonConfig, CoreSysAttributes):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_DNS, SCHEMA_DNS_CONFIG)
        self.coresys: CoreSys = coresys
        self.instance: DockerDNS = DockerDNS(coresys)
        self.forwarder: DNSForward = DNSForward()

    @property
    def servers(self) -> List[str]:
        """Return list of DNS servers."""
        return self._data[ATTR_SERVERS]

    @servers.setter
    def servers(self, value: List[str]) -> None:
        """Return list of DNS servers."""
        self._data[ATTR_SERVERS] = value

    @property
    def version(self) -> Optional[str]:
        """Return current version of DNS."""
        return self._data[ATTR_VERSION]

    @version.setter
    def version(self, value: str) -> None:
        """Return current version of DNS."""
        self._data[ATTR_VERSION] = value

    @property
    def latest_version(self) -> Optional[str]:
        """Return latest version of CoreDNS."""
        return self.sys_updater.version_dns

    async def load(self) -> None:
        """Load DNS setup."""
        try:
            # Evaluate Version if we lost this information
            if not self.version:
                self.version = await self.instance.get_latest_version(key=int)

            await self.instance.attach(tag=self.version)
        except DockerAPIError:
            _LOGGER.info(
                "No CoreDNS plugin Docker image %s found.", self.instance.image
            )
            await self.install()
        else:
            self.version = self.instance.version
            self.save_data()

        # Start DNS forwarder
        self.sys_create_task(self.forwarder.start())

    async def unload(self) -> None:
        """Unload DNS forwarder."""
        await self.forwarder.stop()

    async def install(self) -> None:
        """Install CoreDNS."""
        _LOGGER.info("Setup CoreDNS plugin")
        while True:
            # read homeassistant tag and install it
            if not self.latest_version:
                await self.sys_updater.reload()

            tag = self.latest_version
            if tag:
                with suppress(DockerAPIError):
                    await self.instance.install(tag)
                    break
            _LOGGER.warning("Error on install CoreDNS plugin. Retry in 30sec")
            await asyncio.sleep(30)

        _LOGGER.info("CoreDNS plugin now installed")
        self.version = self.instance.version
        self.save_data()

    async def update(self, version: Optional[str] = None) -> None:
        """Update CoreDNS plugin."""
        version = version or self.latest_version

        if version == self.version:
            _LOGGER.warning("Version %s is already installed for CoreDNS", version)
            return

        try:
            await self.instance.update(version)
        except DockerAPIError:
            _LOGGER.error("CoreDNS update fails")
            raise CoreDNSUpdateError() from None
        else:
            # Cleanup
            with suppress(DockerAPIError):
                await self.instance.cleanup()

    def logs(self) -> Awaitable[bytes]:
        """Get CoreDNS docker logs.

        Return Coroutine.
        """
        return self.instance.logs()

    async def stats(self) -> DockerStats:
        """Return stats of CoreDNS."""
        try:
            return await self.instance.stats()
        except DockerAPIError:
            raise CoreDNSError() from None
