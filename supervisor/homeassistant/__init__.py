"""Home Assistant control object."""
import asyncio
from ipaddress import IPv4Address
import logging
from pathlib import Path
import shutil
from typing import Optional
from uuid import UUID

from ..const import (
    ATTR_ACCESS_TOKEN,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_BOOT,
    ATTR_IMAGE,
    ATTR_PORT,
    ATTR_REFRESH_TOKEN,
    ATTR_SSL,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_WAIT_BOOT,
    ATTR_WATCHDOG,
    FILE_HASSIO_HOMEASSISTANT,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..utils.json import JsonConfig
from ..validate import SCHEMA_HASS_CONFIG
from .api import HomeAssistantAPI
from .core import HomeAssistantCore
from .secrets import HomeAssistantSecrets

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HomeAssistant(JsonConfig, CoreSysAttributes):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize Home Assistant object."""
        super().__init__(FILE_HASSIO_HOMEASSISTANT, SCHEMA_HASS_CONFIG)
        self.coresys: CoreSys = coresys
        self._api: HomeAssistantAPI = HomeAssistantAPI(coresys)
        self._core: HomeAssistantCore = HomeAssistantCore(coresys)
        self._secrets: HomeAssistantSecrets = HomeAssistantSecrets(coresys)

    @property
    def api(self) -> HomeAssistantAPI:
        """Return API handler for core."""
        return self._api

    @property
    def core(self) -> HomeAssistantCore:
        """Return Core handler for docker."""
        return self._core

    @property
    def secrets(self) -> HomeAssistantSecrets:
        """Return Secrets Manager for core."""
        return self._secrets

    @property
    def machine(self) -> str:
        """Return the system machines."""
        return self.core.instance.machine

    @property
    def arch(self) -> str:
        """Return arch of running Home Assistant."""
        return self.core.instance.arch

    @property
    def error_state(self) -> bool:
        """Return True if system is in error."""
        return self.core.error_state

    @property
    def ip_address(self) -> IPv4Address:
        """Return IP of Home Assistant instance."""
        return self.core.instance.ip_address

    @property
    def api_port(self) -> int:
        """Return network port to Home Assistant instance."""
        return self._data[ATTR_PORT]

    @api_port.setter
    def api_port(self, value: int) -> None:
        """Set network port for Home Assistant instance."""
        self._data[ATTR_PORT] = value

    @property
    def api_ssl(self) -> bool:
        """Return if we need ssl to Home Assistant instance."""
        return self._data[ATTR_SSL]

    @api_ssl.setter
    def api_ssl(self, value: bool):
        """Set SSL for Home Assistant instance."""
        self._data[ATTR_SSL] = value

    @property
    def api_url(self) -> str:
        """Return API url to Home Assistant."""
        return "{}://{}:{}".format(
            "https" if self.api_ssl else "http", self.ip_address, self.api_port
        )

    @property
    def watchdog(self) -> bool:
        """Return True if the watchdog should protect Home Assistant."""
        return self._data[ATTR_WATCHDOG]

    @watchdog.setter
    def watchdog(self, value: bool):
        """Return True if the watchdog should protect Home Assistant."""
        self._data[ATTR_WATCHDOG] = value

    @property
    def wait_boot(self) -> int:
        """Return time to wait for Home Assistant startup."""
        return self._data[ATTR_WAIT_BOOT]

    @wait_boot.setter
    def wait_boot(self, value: int):
        """Set time to wait for Home Assistant startup."""
        self._data[ATTR_WAIT_BOOT] = value

    @property
    def latest_version(self) -> str:
        """Return last available version of Home Assistant."""
        return self.sys_updater.version_homeassistant

    @property
    def image(self) -> str:
        """Return image name of the Home Assistant container."""
        if self._data.get(ATTR_IMAGE):
            return self._data[ATTR_IMAGE]
        return f"homeassistant/{self.sys_machine}-homeassistant"

    @image.setter
    def image(self, value: str) -> None:
        """Set image name of Home Assistant container."""
        self._data[ATTR_IMAGE] = value

    @property
    def version(self) -> Optional[str]:
        """Return version of local version."""
        return self._data.get(ATTR_VERSION)

    @version.setter
    def version(self, value: str) -> None:
        """Set installed version."""
        self._data[ATTR_VERSION] = value

    @property
    def boot(self) -> bool:
        """Return True if Home Assistant boot is enabled."""
        return self._data[ATTR_BOOT]

    @boot.setter
    def boot(self, value: bool):
        """Set Home Assistant boot options."""
        self._data[ATTR_BOOT] = value

    @property
    def uuid(self) -> UUID:
        """Return a UUID of this Home Assistant instance."""
        return self._data[ATTR_UUID]

    @property
    def supervisor_token(self) -> Optional[str]:
        """Return an access token for the Supervisor API."""
        return self._data.get(ATTR_ACCESS_TOKEN)

    @supervisor_token.setter
    def supervisor_token(self, value: str) -> None:
        """Set the access token for the Supervisor API."""
        self._data[ATTR_ACCESS_TOKEN] = value

    @property
    def refresh_token(self) -> Optional[str]:
        """Return the refresh token to authenticate with Home Assistant."""
        return self._data.get(ATTR_REFRESH_TOKEN)

    @refresh_token.setter
    def refresh_token(self, value: str):
        """Set Home Assistant refresh_token."""
        self._data[ATTR_REFRESH_TOKEN] = value

    @property
    def path_pulse(self):
        """Return path to asound config."""
        return Path(self.sys_config.path_tmp, "homeassistant_pulse")

    @property
    def path_extern_pulse(self):
        """Return path to asound config for Docker."""
        return Path(self.sys_config.path_extern_tmp, "homeassistant_pulse")

    @property
    def audio_output(self) -> Optional[str]:
        """Return a pulse profile for output or None."""
        return self._data[ATTR_AUDIO_OUTPUT]

    @audio_output.setter
    def audio_output(self, value: Optional[str]):
        """Set audio output profile settings."""
        self._data[ATTR_AUDIO_OUTPUT] = value

    @property
    def audio_input(self) -> Optional[str]:
        """Return pulse profile for input or None."""
        return self._data[ATTR_AUDIO_INPUT]

    @audio_input.setter
    def audio_input(self, value: Optional[str]):
        """Set audio input settings."""
        self._data[ATTR_AUDIO_INPUT] = value

    @property
    def need_update(self) -> bool:
        """Return true if a Home Assistant update is available."""
        if not self.latest_version:
            return False
        return self.version != self.latest_version

    async def load(self) -> None:
        """Prepare Home Assistant object."""
        await asyncio.wait([self.secrets.load(), self.core.load()])

    def write_pulse(self):
        """Write asound config to file and return True on success."""
        pulse_config = self.sys_plugins.audio.pulse_client(
            input_profile=self.audio_input, output_profile=self.audio_output
        )

        # Cleanup wrong maps
        if self.path_pulse.is_dir():
            shutil.rmtree(self.path_pulse, ignore_errors=True)

        # Write pulse config
        try:
            with self.path_pulse.open("w") as config_file:
                config_file.write(pulse_config)
        except OSError as err:
            _LOGGER.error("Home Assistant can't write pulse/client.config: %s", err)
        else:
            _LOGGER.info("Update pulse/client.config: %s", self.path_pulse)
