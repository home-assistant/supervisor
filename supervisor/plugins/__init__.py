"""Plugin for Supervisor backend."""
import asyncio
import logging

from packaging.version import LegacyVersion, parse as pkg_parse

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HassioError
from .audio import Audio
from .cli import HaCli
from .dns import CoreDNS
from .multicast import Multicast
from .observer import Observer

_LOGGER: logging.Logger = logging.getLogger(__name__)


class PluginManager(CoreSysAttributes):
    """Manage supported function for plugins."""

    required_cli: LegacyVersion = pkg_parse("2020.10.0")
    required_dns: LegacyVersion = pkg_parse("9")
    required_audio: LegacyVersion = pkg_parse("17")
    required_observer: LegacyVersion = pkg_parse("2020.10.1")
    required_multicast: LegacyVersion = pkg_parse("3")

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
                self.sys_capture_exception(err)

        # Check requirements
        for plugin, required_version in (
            (self._audio, self.required_audio),
            (self._dns, self.required_dns),
            (self._cli, self.required_cli),
            (self._observer, self.required_observer),
            (self._multicast, self.required_multicast),
        ):
            # Check if need an update
            try:
                if pkg_parse(plugin.version) >= required_version:
                    continue
            except TypeError:
                _LOGGER.warning(
                    "Unexpected issue while checking requirements for %s",
                    type(plugin).__name__,
                )

            _LOGGER.info(
                "%s does not have the required version %s, updating",
                type(plugin).__name__,
                required_version,
            )
            try:
                await plugin.update(version=str(required_version))
            except HassioError:
                _LOGGER.error(
                    "Can't update %s to %s but it's a reuirement, the Supervisor is now in an unhealthy state!",
                    type(plugin).__name__,
                    required_version,
                )
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning(
                    "Can't update plugin %s: %s", type(plugin).__name__, err
                )
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
