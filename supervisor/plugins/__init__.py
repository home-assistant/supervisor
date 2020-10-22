"""Plugin for Supervisor backend."""
import asyncio
import logging

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HassioError
from ..resolution.const import ContextType, IssueType, SuggestionType
from .audio import Audio
from .cli import HaCli
from .dns import CoreDNS
from .multicast import Multicast
from .observer import Observer

_LOGGER: logging.Logger = logging.getLogger(__name__)


class PluginManager(CoreSysAttributes):
    """Manage supported function for plugins."""

    def __init__(self, coresys: CoreSys):
        """Initialize plugin manager."""
        self.coresys: CoreSys = coresys

        self._cli: HaCli = HaCli(coresys)
        self._dns: CoreDNS = CoreDNS(coresys)
        self._audio: Audio = Audio(coresys)
        self._observer: Observer = Observer(coresys)
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
    def observer(self) -> Observer:
        """Return observer handler."""
        return self._observer

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
            self.observer,
            self.multicast,
        ):
            try:
                await plugin.load()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't load plugin %s: %s", type(plugin).__name__, err)
                self.sys_resolution.create_issue(
                    IssueType.FATAL_ERROR,
                    ContextType.PLUGIN,
                    reference=plugin.slug,
                    suggestions=[SuggestionType.EXECUTE_REPAIR],
                )
                self.sys_capture_exception(err)

        # Check requirements
        await self.sys_updater.reload()
        for plugin in (
            self.dns,
            self.audio,
            self.cli,
            self.observer,
            self.multicast,
        ):
            # Check if need an update
            if not plugin.need_update:
                continue

            _LOGGER.info(
                "%s does not have the latest version %s, updating",
                plugin.slug,
                plugin.latest_version,
            )
            try:
                await plugin.update()
            except HassioError:
                _LOGGER.error(
                    "Can't update %s to %s, the Supervisor healthy could be compromised!",
                    plugin.slug,
                    plugin.latest_version,
                )
                self.sys_resolution.create_issue(
                    IssueType.UPDATE_FAILED,
                    ContextType.PLUGIN,
                    reference=plugin.slug,
                    suggestions=[SuggestionType.EXECUTE_UPDATE],
                )
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't update plugin %s: %s", plugin.slug, err)
                self.sys_capture_exception(err)

    async def repair(self) -> None:
        """Repair Supervisor plugins."""
        await asyncio.wait(
            [
                self.dns.repair(),
                self.audio.repair(),
                self.cli.repair(),
                self.observer.repair(),
                self.multicast.repair(),
            ]
        )

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
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't stop plugin %s: %s", type(plugin).__name__, err)
                self.sys_capture_exception(err)
