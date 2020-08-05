"""Plugin for Supervisor backend."""
import asyncio
import logging

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HassioError
from .audio import Audio
from .cli import HaCli
from .dns import CoreDNS
from .multicast import Multicast

_LOGGER: logging.Logger = logging.getLogger(__name__)


class PluginManager(CoreSysAttributes):
    """Manage supported function for plugins."""

    required_cli: int = 25
    required_dns: int = 9
    required_audio: int = 16
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

    async def load(self) -> None:
        """Load Supervisor plugins."""
        # Sequential to avoid issue on slow IO
        for plugin in (
            self.dns,
            self.audio,
            self.cli,
            self.multicast,
        ):
            try:
                await plugin.load()
            except Exception:  # pylint: disable=broad-except
                _LOGGER.warning("Can't load plugin %s", type(plugin).__name__)

        # Check requirements
        for plugin, required_version in (
            (self._audio, self.required_audio),
            (self._dns, self.required_dns),
            (self._cli, self.required_cli),
            (self._multicast, self.required_multicast),
        ):
            # Check if need an update
            try:
                if int(plugin.version) >= required_version:
                    continue
            except (TypeError, ValueError):
                if plugin.version == "dev":
                    continue
                _LOGGER.warning(
                    "Somethings going wrong with requirements on %s",
                    type(plugin).__name__,
                )

            _LOGGER.info(
                "Requirement need update for %s - %i",
                type(plugin).__name__,
                required_version,
            )
            try:
                await plugin.update(version=str(required_version))
            except HassioError:
                _LOGGER.error(
                    "Can't update %s to %i but it's a reuirement, the Supervisor is not health now!",
                    type(plugin).__name__,
                    required_version,
                )

    async def repair(self) -> None:
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
        # Sequential to avoid issue on slow IO
        for plugin in (
            self.audio,
            self.cli,
            self.multicast,
            self.dns,
        ):
            try:
                await plugin.stop()
            except Exception:  # pylint: disable=broad-except
                _LOGGER.warning("Can't stop plugin %s", type(plugin).__name__)
