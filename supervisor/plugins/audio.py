"""Home Assistant audio plugin.

Code: https://github.com/home-assistant/plugin-audio
"""

import logging
from pathlib import Path, PurePath
import shutil

from awesomeversion import AwesomeVersion
import jinja2

from ..const import LogLevel
from ..coresys import CoreSys
from ..docker.audio import DockerAudio
from ..docker.const import ContainerState
from ..exceptions import (
    AudioConfigError,
    AudioDisabledError,
    AudioJobError,
    AudioNotInstalledError,
    AudioNotRunningError,
    AudioRestartError,
    AudioStartError,
    AudioStatsTimeoutError,
    AudioStopError,
    AudioUnknownError,
    AudioUpdateAlreadyInstalledError,
    AudioUpdateError,
    ConfigurationFileError,
)
from ..jobs.const import JobThrottle
from ..jobs.decorator import Job
from ..utils.json import write_json_file
from .base import PluginBase, PluginErrors
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

    errors = PluginErrors(
        start=AudioStartError,
        stop=AudioStopError,
        update=AudioUpdateError,
        restart=AudioRestartError,
        not_running=AudioNotRunningError,
        stats_timeout=AudioStatsTimeoutError,
        unknown=AudioUnknownError,
        not_installed=AudioNotInstalledError,
        already_installed=AudioUpdateAlreadyInstalledError,
        disabled=AudioDisabledError,
    )

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
            self.sys_resolution.check_oserror(err)
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
            self.sys_resolution.check_oserror(err)
            _LOGGER.error("Can't create default asound: %s", err)

    @Job(
        name="plugin_audio_update",
        conditions=PLUGIN_UPDATE_CONDITIONS,
        on_condition=AudioJobError,
    )
    async def update(self, version: str | None = None) -> None:
        """Update Audio plugin."""
        await super().update(version)

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
            raise AudioConfigError(_LOGGER.error) from err

    @Job(
        name="plugin_audio_restart_after_problem",
        throttle_period=WATCHDOG_THROTTLE_PERIOD,
        throttle_max_calls=WATCHDOG_THROTTLE_MAX_CALLS,
        on_condition=AudioJobError,
        throttle=JobThrottle.RATE_LIMIT,
    )
    async def _restart_after_problem(
        self, state: ContainerState, exit_code: int | None = None
    ):
        """Restart unhealthy or failed plugin."""
        return await super()._restart_after_problem(state, exit_code)
