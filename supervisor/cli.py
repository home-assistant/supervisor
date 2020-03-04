"""CLI support on supervisor."""
from contextlib import suppress
import logging
from typing import Optional

from .coresys import CoreSysAttributes, CoreSys
from .docker.cli import DockerCli
from .exceptions import (
    CliUpdateError,
    DockerAPIError,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HaCli(CoreSysAttributes):
    """HA cli interface inside supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize cli handler."""
        self.coresys: CoreSys = coresys
        self.instance: DockerCli = DockerCli(coresys)

    @property
    def version(self) -> Optional[str]:
        """Return version of cli."""
        return self.instance.version

    @property
    def version_latest(self) -> str:
        """Return version of latest cli."""
        return self.sys_updater.version_cli

    @property
    def need_update(self) -> bool:
        """Return true if a cli update is available."""
        return self.version != self.version_latest

    async def load(self) -> None:
        """Load HassOS data."""
        with suppress(DockerAPIError):
            await self.instance.attach(tag="latest")

    async def update(self, version: Optional[str] = None) -> None:
        """Update local HA cli."""
        version = version or self.version_latest

        if version == self.version:
            _LOGGER.warning("Version %s is already installed for cli", version)
            return

        try:
            await self.instance.update(version, latest=True)
        except DockerAPIError:
            _LOGGER.error("HA cli update fails")
            raise CliUpdateError() from None
        else:
            # Cleanup
            with suppress(DockerAPIError):
                await self.instance.cleanup()

    async def repair(self) -> None:
        """Repair cli container."""
        if await self.instance.exists():
            return
        version = self.version or self.version_latest

        _LOGGER.info("Repair HA cli %s", version)
        try:
            await self.instance.install(version, latest=True)
        except DockerAPIError:
            _LOGGER.error("Repairing of HA cli fails")
