"""Plugin for Supervisor backend."""
import asyncio
import logging
from typing import Awaitable

from ..coresys import CoreSys, CoreSysAttributes
from .audio import Audio
from .cli import HaCli
from .dns import CoreDNS
from .multicast import Multicast

_LOGGER: logging.Logger = logging.getLogger(__name__)


class PluginManager(CoreSysAttributes):
    """Manage supported function for plugins."""

    required_cli: int = 24
    required_dns: int = 5
    required_audio: int = 14
    required_multicast: int = 2

    def __init__(self, coresys: CoreSys):
        """Initialize plugin manager."""
        self.coresys: CoreSys = coresys

        self._cli: HaCli = HaCli(coresys)
        self._dns: CoreDNS = CoreDNS(coresys)
        self._audio: Audio = Audio(coresys)
        self._multicast: Multicast = Multicast(coresys)

    @property
    def cli(self) -> HaCli:
        """Return cli handler."""
        return self._cli

    @property
    def dns(self) -> CoreDNS:
        """Return dns handler."""
        return self._dns

    @property
    def audio(self) -> Audio:
        """Return audio handler."""
        return self._audio

    @property
    def multicast(self) -> Multicast:
        """Return multicast handler."""
        return self._multicast

    async def load(self):
        """Load Supervisor plugins."""
        await asyncio.wait(
            [self.dns.load(), self.audio.load(), self.cli.load(), self.multicast.load()]
        )

        # Check requirements
        update_tasks: Awaitable[None] = []
        for plugin, required_version in (
            (self._audio, self.required_audio),
            (self._dns, self.required_dns),
            (self._cli, self.required_cli),
            (self._multicast, self.required_multicast),
        ):
            try:
                if int(plugin.version) < required_version:
                    update_tasks.append(plugin.update(version=str(required_version)))
                    _LOGGER.info(
                        "Requirement need update for %s - %i",
                        type(plugin).__name__,
                        required_version,
                    )
            except TypeError:
                _LOGGER.warning(
                    "Somethings going wrong with requirements on %s",
                    type(plugin).__name__,
                )

        if update_tasks:
            await asyncio.wait(update_tasks)

    async def repair(self):
        """Repair Supervisor plugins."""
        await asyncio.wait(
            [
                self.dns.repair(),
                self.audio.repair(),
                self.cli.repair(),
                self.multicast.repair(),
            ]
        )

    async def unload(self) -> None:
        """Unload Supervisor plugin."""
        await asyncio.wait([self.dns.unload()])

    async def shutdown(self) -> None:
        """Shutdown Supervisor plugin."""
        await asyncio.wait(
            [
                self.dns.stop(),
                self.audio.stop(),
                self.cli.stop(),
                self.multicast.stop(),
            ]
        )
