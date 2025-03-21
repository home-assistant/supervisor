"""Home Assistant audio plugin.

Code: https://github.com/home-assistant/plugin-audio
"""

import errno
import logging
from pathlib import Path, PurePath
import shutil

from awesomeversion import AwesomeVersion
import jinja2

from ..const import LogLevel
from ..coresys import CoreSys
from ..docker.audio import DockerAudio
from ..docker.const import ContainerState
from ..docker.stats import DockerStats
from ..exceptions import (
    AudioError,
    AudioJobError,
    AudioUpdateError,
    ConfigurationFileError,
    DockerError,
)
from ..jobs.const import JobExecutionLimit
from ..jobs.decorator import Job
from ..resolution.const import UnhealthyReason
from ..utils.json import write_json_file
from ..utils.sentry import async_capture_exception
from .base import PluginBase
from .const import (
    FILE_HASSIO_AUDIO,
    PLUGIN_UPDATE_CONDITIONS,
    WATCHDOG_THROTTLE_MAX_CALLS,
    WATCHDOG_THROTTLE_PERIOD,
)
from .validate import SCHEMA_AUDIO_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)

# pylint: disable=no-member
PULSE_CLIENT_TMPL: Path = Path(__file__).parents[1].joinpath("data/pulse-client.tmpl")
ASOUND_TMPL: Path = Path(__file__).parents[1].joinpath("data/asound.tmpl")
# pylint: enable=no-member


class PluginAudio(PluginBase):
    """Home Assistant core object for handle audio."""

    def __init__(self, coresys: CoreSys):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_AUDIO, SCHEMA_AUDIO_CONFIG)
        self.slug = "audio"
        self.coresys: CoreSys = coresys
        self.instance: DockerAudio = DockerAudio(coresys)
        self.client_template: jinja2.Template | None = None

    @property
    def path_extern_pulse(self) -> PurePath:
        """Return path of pulse socket file."""
        return self.sys_config.path_extern_audio.joinpath("external")

    @property
    def path_extern_asound(self) -> PurePath:
        """Return path of default asound config file."""
        return self.sys_config.path_extern_audio.joinpath("asound")

    @property
    def pulse_audio_config(self) -> Path:
        """Return Path to pulse audio config file."""
        return Path(self.sys_config.path_audio, "pulse_audio.json")

    @property
    def default_image(self) -> str:
        """Return default image for audio plugin."""
        if self.sys_updater.image_audio:
            return self.sys_updater.image_audio
        return super().default_image

    @property
    def latest_version(self) -> AwesomeVersion | None:
        """Return latest version of Audio."""
        return self.sys_updater.version_audio

    async def load(self) -> None:
        """Load Audio setup."""
        # Initialize Client Template
        try:
            self.client_template = jinja2.Template(
                await self.sys_run_in_executor(
                    PULSE_CLIENT_TMPL.read_text, encoding="utf-8"
                )
            )
        except OSError as err:
            if err.errno == errno.EBADMSG:
                self.sys_resolution.add_unhealthy_reason(
                    UnhealthyReason.OSERROR_BAD_MESSAGE
                )

            _LOGGER.error("Can't read pulse-client.tmpl: %s", err)

        await super().load()

        # Setup default asound config
        asound = self.sys_config.path_audio.joinpath("asound")

        def setup_default_asound():
            if not asound.exists():
                shutil.copy(ASOUND_TMPL, asound)

        try:
            await self.sys_run_in_executor(setup_default_asound)
        except OSError as err:
            if err.errno == errno.EBADMSG:
                self.sys_resolution.add_unhealthy_reason(
                    UnhealthyReason.OSERROR_BAD_MESSAGE
                )
            _LOGGER.error("Can't create default asound: %s", err)

    @Job(
        name="plugin_audio_update",
        conditions=PLUGIN_UPDATE_CONDITIONS,
        on_condition=AudioJobError,
    )
    async def update(self, version: str | None = None) -> None:
        """Update Audio plugin."""
        try:
            await super().update(version)
        except DockerError as err:
            raise AudioUpdateError("Audio update failed", _LOGGER.error) from err

    async def restart(self) -> None:
        """Restart Audio plugin."""
        _LOGGER.info("Restarting Audio plugin")
        await self._write_config()
        try:
            await self.instance.restart()
        except DockerError as err:
            raise AudioError("Can't start Audio plugin", _LOGGER.error) from err

    async def start(self) -> None:
        """Run Audio plugin."""
        _LOGGER.info("Starting Audio plugin")
        await self._write_config()
        try:
            await self.instance.run()
        except DockerError as err:
            raise AudioError("Can't start Audio plugin", _LOGGER.error) from err

    async def stop(self) -> None:
        """Stop Audio plugin."""
        _LOGGER.info("Stopping Audio plugin")
        try:
            await self.instance.stop()
        except DockerError as err:
            raise AudioError("Can't stop Audio plugin", _LOGGER.error) from err

    async def stats(self) -> DockerStats:
        """Return stats of Audio plugin."""
        try:
            return await self.instance.stats()
        except DockerError as err:
            raise AudioError() from err

    async def repair(self) -> None:
        """Repair Audio plugin."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repairing Audio %s", self.version)
        try:
            await self.instance.install(self.version)
        except DockerError as err:
            _LOGGER.error("Repair of Audio failed")
            await async_capture_exception(err)

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

    async def _write_config(self):
        """Write pulse audio config."""
        try:
            await self.sys_run_in_executor(
                write_json_file,
                self.pulse_audio_config,
                {
                    "debug": self.sys_config.logging == LogLevel.DEBUG,
                },
            )
        except ConfigurationFileError as err:
            raise AudioError(
                f"Can't update pulse audio config: {err}", _LOGGER.error
            ) from err

    @Job(
        name="plugin_audio_restart_after_problem",
        limit=JobExecutionLimit.THROTTLE_RATE_LIMIT,
        throttle_period=WATCHDOG_THROTTLE_PERIOD,
        throttle_max_calls=WATCHDOG_THROTTLE_MAX_CALLS,
        on_condition=AudioJobError,
    )
    async def _restart_after_problem(self, state: ContainerState):
        """Restart unhealthy or failed plugin."""
        return await super()._restart_after_problem(state)
