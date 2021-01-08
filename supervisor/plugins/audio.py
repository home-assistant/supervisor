"""Home Assistant audio plugin.

Code: https://github.com/home-assistant/plugin-audio
"""
import asyncio
from contextlib import suppress
import logging
from pathlib import Path, PurePath
import shutil
from typing import Awaitable, Optional

from awesomeversion import AwesomeVersion
import jinja2

from ..coresys import CoreSys
from ..docker.audio import DockerAudio
from ..docker.stats import DockerStats
from ..exceptions import AudioError, AudioUpdateError, DockerError
from .base import PluginBase
from .const import FILE_HASSIO_AUDIO
from .validate import SCHEMA_AUDIO_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)

PULSE_CLIENT_TMPL: Path = Path(__file__).parents[1].joinpath("data/pulse-client.tmpl")
ASOUND_TMPL: Path = Path(__file__).parents[1].joinpath("data/asound.tmpl")


class PluginAudio(PluginBase):
    """Home Assistant core object for handle audio."""

    def __init__(self, coresys: CoreSys):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_AUDIO, SCHEMA_AUDIO_CONFIG)
        self.slug = "audio"
        self.coresys: CoreSys = coresys
        self.instance: DockerAudio = DockerAudio(coresys)
        self.client_template: Optional[jinja2.Template] = None

    @property
    def path_extern_pulse(self) -> PurePath:
        """Return path of pulse socket file."""
        return self.sys_config.path_extern_audio.joinpath("external")

    @property
    def path_extern_asound(self) -> PurePath:
        """Return path of default asound config file."""
        return self.sys_config.path_extern_audio.joinpath("asound")

    @property
    def latest_version(self) -> Optional[AwesomeVersion]:
        """Return latest version of Audio."""
        return self.sys_updater.version_audio

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    async def load(self) -> None:
        """Load Audio setup."""
        # Initialize Client Template
        try:
            self.client_template = jinja2.Template(PULSE_CLIENT_TMPL.read_text())
        except OSError as err:
            _LOGGER.error("Can't read pulse-client.tmpl: %s", err)

        # Check Audio state
        try:
            # Evaluate Version if we lost this information
            if not self.version:
                self.version = await self.instance.get_latest_version()

            await self.instance.attach(version=self.version)
        except DockerError:
            _LOGGER.info("No Audio plugin Docker image %s found.", self.instance.image)

            # Install PulseAudio
            with suppress(AudioError):
                await self.install()
        else:
            self.version = self.instance.version
            self.image = self.instance.image
            self.save_data()

        # Run PulseAudio
        with suppress(AudioError):
            if not await self.instance.is_running():
                await self.start()

        # Setup default asound config
        asound = self.sys_config.path_audio.joinpath("asound")
        if not asound.exists():
            try:
                shutil.copy(ASOUND_TMPL, asound)
            except OSError as err:
                _LOGGER.error("Can't create default asound: %s", err)

    async def install(self) -> None:
        """Install Audio."""
        _LOGGER.info("Setup Audio plugin")
        while True:
            # read audio tag and install it
            if not self.latest_version:
                await self.sys_updater.reload()

            if self.latest_version:
                with suppress(DockerError):
                    await self.instance.install(
                        self.latest_version, image=self.sys_updater.image_audio
                    )
                    break
            _LOGGER.warning("Error on installing Audio plugin, retrying in 30sec")
            await asyncio.sleep(30)

        _LOGGER.info("Audio plugin now installed")
        self.version = self.instance.version
        self.image = self.sys_updater.image_audio
        self.save_data()

    async def update(self, version: Optional[str] = None) -> None:
        """Update Audio plugin."""
        version = version or self.latest_version
        old_image = self.image

        if version == self.version:
            _LOGGER.warning("Version %s is already installed for Audio", version)
            return

        try:
            await self.instance.update(version, image=self.sys_updater.image_audio)
        except DockerError as err:
            _LOGGER.error("Audio update failed")
            raise AudioUpdateError() from err
        else:
            self.version = version
            self.image = self.sys_updater.image_audio
            self.save_data()

        # Cleanup
        with suppress(DockerError):
            await self.instance.cleanup(old_image=old_image)

        # Start Audio
        await self.start()

    async def restart(self) -> None:
        """Restart Audio plugin."""
        _LOGGER.info("Restarting Audio plugin")
        try:
            await self.instance.restart()
        except DockerError as err:
            _LOGGER.error("Can't start Audio plugin")
            raise AudioError() from err

    async def start(self) -> None:
        """Run CoreDNS."""
        _LOGGER.info("Starting Audio plugin")
        try:
            await self.instance.run()
        except DockerError as err:
            _LOGGER.error("Can't start Audio plugin")
            raise AudioError() from err

    async def stop(self) -> None:
        """Stop CoreDNS."""
        _LOGGER.info("Stopping Audio plugin")
        try:
            await self.instance.stop()
        except DockerError as err:
            _LOGGER.error("Can't stop Audio plugin")
            raise AudioError() from err

    def logs(self) -> Awaitable[bytes]:
        """Get CoreDNS docker logs.

        Return Coroutine.
        """
        return self.instance.logs()

    async def stats(self) -> DockerStats:
        """Return stats of CoreDNS."""
        try:
            return await self.instance.stats()
        except DockerError as err:
            raise AudioError() from err

    def is_running(self) -> Awaitable[bool]:
        """Return True if Docker container is running.

        Return a coroutine.
        """
        return self.instance.is_running()

    async def repair(self) -> None:
        """Repair CoreDNS plugin."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repairing Audio %s", self.version)
        try:
            await self.instance.install(self.version)
        except DockerError as err:
            _LOGGER.error("Repair of Audio failed")
            self.sys_capture_exception(err)

    def pulse_client(self, input_profile=None, output_profile=None) -> str:
        """Generate an /etc/pulse/client.conf data."""
        if self.client_template is None:
            return ""

        # Process Template
        return self.client_template.render(
            audio_address=self.sys_docker.network.audio,
            default_source=input_profile,
            default_sink=output_profile,
        )
