"""Home Assistant control object."""
import asyncio
from contextlib import suppress
import logging
from pathlib import Path
from string import Template
from typing import Awaitable, List, Optional

from .const import ATTR_VERSION, FILE_HASSIO_AUDIO
from .coresys import CoreSys, CoreSysAttributes
from .docker.audio import DockerAudio
from .docker.stats import DockerStats
from .exceptions import AudioError, AudioUpdateError, DockerAPIError
from .utils.json import JsonConfig
from .validate import SCHEMA_AUDIO_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)

PULSE_CLIENT_TMPL: Path = Path(__file__).parents[0].joinpath("data/pulse-client.tmpl")


class Audio(JsonConfig, CoreSysAttributes):
    """Home Assistant core object for handle audio."""

    def __init__(self, coresys: CoreSys):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_AUDIO, SCHEMA_AUDIO_CONFIG)
        self.coresys: CoreSys = coresys
        self.instance: DockerAudio = DockerAudio(coresys)

    @property
    def path_extern_cookie(self) -> Path:
        """Return path of pulse cookie file."""
        return self.sys_config.path_extern_audio.joinpath("cookie")

    @property
    def version(self) -> Optional[str]:
        """Return current version of Audio."""
        return self._data.get(ATTR_VERSION)

    @version.setter
    def version(self, value: str) -> None:
        """Return current version of Audio."""
        self._data[ATTR_VERSION] = value

    @property
    def latest_version(self) -> Optional[str]:
        """Return latest version of Audio."""
        return self.sys_updater.version_audio

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    @property
    def need_update(self) -> bool:
        """Return True if an update is available."""
        return self.version != self.latest_version

    async def load(self) -> None:
        """Load Audio setup."""

        # Check Audio state
        try:
            # Evaluate Version if we lost this information
            if not self.version:
                self.version = await self.instance.get_latest_version(key=int)

            await self.instance.attach(tag=self.version)
        except DockerAPIError:
            _LOGGER.info("No Audio plugin Docker image %s found.", self.instance.image)

            # Install CoreDNS
            with suppress(AudioError):
                await self.install()
        else:
            self.version = self.instance.version
            self.save_data()

        # Run CoreDNS
        with suppress(AudioError):
            if await self.instance.is_running():
                await self.restart()
            else:
                await self.start()

    async def install(self) -> None:
        """Install Audio."""
        _LOGGER.info("Setup Audio plugin")
        while True:
            # read audio tag and install it
            if not self.latest_version:
                await self.sys_updater.reload()

            if self.latest_version:
                with suppress(DockerAPIError):
                    await self.instance.install(self.latest_version)
                    break
            _LOGGER.warning("Error on install Audio plugin. Retry in 30sec")
            await asyncio.sleep(30)

        _LOGGER.info("Audio plugin now installed")
        self.version = self.instance.version
        self.save_data()

    async def update(self, version: Optional[str] = None) -> None:
        """Update Audio plugin."""
        version = version or self.latest_version

        if version == self.version:
            _LOGGER.warning("Version %s is already installed for Audio", version)
            return

        try:
            await self.instance.update(version)
        except DockerAPIError:
            _LOGGER.error("Audio update fails")
            raise AudioUpdateError() from None
        else:
            # Cleanup
            with suppress(DockerAPIError):
                await self.instance.cleanup()

        self.version = version
        self.save_data()

        # Start Audio
        await self.start()

    async def restart(self) -> None:
        """Restart Audio plugin."""
        with suppress(DockerAPIError):
            await self.instance.restart()

    async def start(self) -> None:
        """Run CoreDNS."""
        # Start Instance
        _LOGGER.info("Start Audio plugin")
        try:
            await self.instance.run()
        except DockerAPIError:
            _LOGGER.error("Can't start Audio plugin")
            raise AudioError() from None

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
            raise AudioError() from None

    def is_running(self) -> Awaitable[bool]:
        """Return True if Docker container is running.

        Return a coroutine.
        """
        return self.instance.is_running()

    def is_fails(self) -> Awaitable[bool]:
        """Return True if a Docker container is fails state.

        Return a coroutine.
        """
        return self.instance.is_fails()

    async def repair(self) -> None:
        """Repair CoreDNS plugin."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repair Audio %s", self.version)
        try:
            await self.instance.install(self.version)
        except DockerAPIError:
            _LOGGER.error("Repairing of Audio fails")

    def pulse_client(self, input_profile=None, output_profile=None) -> str:
        """Generate an /etc/pulse/client.conf data."""

        # Read Template
        try:
            config_data = PULSE_CLIENT_TMPL.read_text()
        except OSError as err:
            _LOGGER.error("Can't read pulse-client.tmpl: %s", err)
            return ""

        # Process Template
        config_template = Template(config_data)
        return config_template.safe_substitute(
            audio_address=self.sys_docker.network.audio
        )
