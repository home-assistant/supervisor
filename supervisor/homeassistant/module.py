"""Home Assistant control object."""

import asyncio
from datetime import timedelta
import errno
from ipaddress import IPv4Address
import logging
from pathlib import Path, PurePath
import shutil
import tarfile
from tempfile import TemporaryDirectory
from typing import Any
from uuid import UUID

from awesomeversion import AwesomeVersion, AwesomeVersionException
from securetar import AddFileError, atomic_contents_add, secure_path
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..const import (
    ATTR_ACCESS_TOKEN,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_BACKUPS_EXCLUDE_DATABASE,
    ATTR_BOOT,
    ATTR_IMAGE,
    ATTR_MESSAGE,
    ATTR_PORT,
    ATTR_REFRESH_TOKEN,
    ATTR_SSL,
    ATTR_TYPE,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_WATCHDOG,
    FILE_HASSIO_HOMEASSISTANT,
    BusEvent,
    IngressSessionDataUser,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    ConfigurationFileError,
    HomeAssistantBackupError,
    HomeAssistantError,
    HomeAssistantWSError,
)
from ..hardware.const import PolicyGroup
from ..hardware.data import Device
from ..jobs.decorator import Job, JobExecutionLimit
from ..resolution.const import UnhealthyReason
from ..utils import remove_folder, remove_folder_with_excludes
from ..utils.common import FileConfiguration
from ..utils.json import read_json_file, write_json_file
from .api import HomeAssistantAPI
from .const import ATTR_ERROR, ATTR_OVERRIDE_IMAGE, ATTR_SUCCESS, LANDINGPAGE, WSType
from .core import HomeAssistantCore
from .secrets import HomeAssistantSecrets
from .validate import SCHEMA_HASS_CONFIG
from .websocket import HomeAssistantWebSocket

_LOGGER: logging.Logger = logging.getLogger(__name__)


HOMEASSISTANT_BACKUP_EXCLUDE = [
    "**/__pycache__/*",
    "**/.DS_Store",
    "*.db-shm",
    "*.corrupt.*",
    "*.log.*",
    "*.log",
    ".storage/*.corrupt.*",
    "OZW_Log.txt",
    "backups/*.tar",
    "tmp_backups/*.tar",
    "tts/*",
]
HOMEASSISTANT_BACKUP_EXCLUDE_DATABASE = [
    "home-assistant_v?.db",
    "home-assistant_v?.db-wal",
]


class HomeAssistant(FileConfiguration, CoreSysAttributes):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize Home Assistant object."""
        super().__init__(FILE_HASSIO_HOMEASSISTANT, SCHEMA_HASS_CONFIG)
        self.coresys: CoreSys = coresys
        self._api: HomeAssistantAPI = HomeAssistantAPI(coresys)
        self._websocket: HomeAssistantWebSocket = HomeAssistantWebSocket(coresys)
        self._core: HomeAssistantCore = HomeAssistantCore(coresys)
        self._secrets: HomeAssistantSecrets = HomeAssistantSecrets(coresys)

    @property
    def api(self) -> HomeAssistantAPI:
        """Return API handler for core."""
        return self._api

    @property
    def websocket(self) -> HomeAssistantWebSocket:
        """Return Websocket handler for core."""
        return self._websocket

    @property
    def core(self) -> HomeAssistantCore:
        """Return Core handler for docker."""
        return self._core

    @property
    def secrets(self) -> HomeAssistantSecrets:
        """Return Secrets Manager for core."""
        return self._secrets

    @property
    def machine(self) -> str | None:
        """Return the system machines."""
        return self.core.instance.machine

    @property
    def arch(self) -> str | None:
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
        return (
            f"{'https' if self.api_ssl else 'http'}://{self.ip_address}:{self.api_port}"
        )

    @property
    def ws_url(self) -> str:
        """Return API url to Home Assistant."""
        return f"{'wss' if self.api_ssl else 'ws'}://{self.ip_address}:{self.api_port}/api/websocket"

    @property
    def watchdog(self) -> bool:
        """Return True if the watchdog should protect Home Assistant."""
        return self._data[ATTR_WATCHDOG]

    @watchdog.setter
    def watchdog(self, value: bool):
        """Return True if the watchdog should protect Home Assistant."""
        self._data[ATTR_WATCHDOG] = value

    @property
    def latest_version(self) -> AwesomeVersion | None:
        """Return last available version of Home Assistant."""
        return self.sys_updater.version_homeassistant

    @property
    def default_image(self) -> str:
        """Return the default image for this system."""
        return f"ghcr.io/home-assistant/{self.sys_machine}-homeassistant"

    @property
    def image(self) -> str:
        """Return image name of the Home Assistant container."""
        if self._data.get(ATTR_IMAGE):
            return self._data[ATTR_IMAGE]
        return self.default_image

    def set_image(self, value: str | None) -> None:
        """Set image name of Home Assistant container."""
        self._data[ATTR_IMAGE] = value

    @property
    def override_image(self) -> bool:
        """Return if user has overridden the image to use for Home Assistant."""
        return self._data[ATTR_OVERRIDE_IMAGE]

    @override_image.setter
    def override_image(self, value: bool) -> None:
        """Enable/disable image override."""
        self._data[ATTR_OVERRIDE_IMAGE] = value

    @property
    def version(self) -> AwesomeVersion | None:
        """Return version of local version."""
        return self._data.get(ATTR_VERSION)

    @version.setter
    def version(self, value: AwesomeVersion) -> None:
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
    def supervisor_token(self) -> str | None:
        """Return an access token for the Supervisor API."""
        return self._data.get(ATTR_ACCESS_TOKEN)

    @supervisor_token.setter
    def supervisor_token(self, value: str) -> None:
        """Set the access token for the Supervisor API."""
        self._data[ATTR_ACCESS_TOKEN] = value

    @property
    def refresh_token(self) -> str | None:
        """Return the refresh token to authenticate with Home Assistant."""
        return self._data.get(ATTR_REFRESH_TOKEN)

    @refresh_token.setter
    def refresh_token(self, value: str | None):
        """Set Home Assistant refresh_token."""
        self._data[ATTR_REFRESH_TOKEN] = value

    @property
    def path_pulse(self) -> Path:
        """Return path to asound config."""
        return Path(self.sys_config.path_tmp, "homeassistant_pulse")

    @property
    def path_extern_pulse(self) -> PurePath:
        """Return path to asound config for Docker."""
        return PurePath(self.sys_config.path_extern_tmp, "homeassistant_pulse")

    @property
    def audio_output(self) -> str | None:
        """Return a pulse profile for output or None."""
        return self._data[ATTR_AUDIO_OUTPUT]

    @audio_output.setter
    def audio_output(self, value: str | None):
        """Set audio output profile settings."""
        self._data[ATTR_AUDIO_OUTPUT] = value

    @property
    def audio_input(self) -> str | None:
        """Return pulse profile for input or None."""
        return self._data[ATTR_AUDIO_INPUT]

    @audio_input.setter
    def audio_input(self, value: str | None):
        """Set audio input settings."""
        self._data[ATTR_AUDIO_INPUT] = value

    @property
    def need_update(self) -> bool:
        """Return true if a Home Assistant update is available."""
        try:
            return self.version is not None and self.version < self.latest_version
        except (AwesomeVersionException, TypeError):
            return False

    @property
    def backups_exclude_database(self) -> bool:
        """Exclude database from core backups by default."""
        return self._data[ATTR_BACKUPS_EXCLUDE_DATABASE]

    @backups_exclude_database.setter
    def backups_exclude_database(self, value: bool) -> None:
        """Set whether backups should exclude database by default."""
        self._data[ATTR_BACKUPS_EXCLUDE_DATABASE] = value

    async def load(self) -> None:
        """Prepare Home Assistant object."""
        await asyncio.wait(
            [
                self.sys_create_task(self.websocket.load()),
                self.sys_create_task(self.secrets.load()),
                self.sys_create_task(self.core.load()),
            ]
        )

        # Register for events
        self.sys_bus.register_event(BusEvent.HARDWARE_NEW_DEVICE, self._hardware_events)
        self.sys_bus.register_event(
            BusEvent.HARDWARE_REMOVE_DEVICE, self._hardware_events
        )

    async def write_pulse(self):
        """Write asound config to file and return True on success."""
        pulse_config = self.sys_plugins.audio.pulse_client(
            input_profile=self.audio_input, output_profile=self.audio_output
        )

        def write_pulse_config():
            # Cleanup wrong maps
            if self.path_pulse.is_dir():
                shutil.rmtree(self.path_pulse, ignore_errors=True)
            self.path_pulse.write_text(pulse_config, encoding="utf-8")

        try:
            await self.sys_run_in_executor(write_pulse_config)
        except OSError as err:
            if err.errno == errno.EBADMSG:
                self.sys_resolution.add_unhealthy_reason(
                    UnhealthyReason.OSERROR_BAD_MESSAGE
                )
            _LOGGER.error("Home Assistant can't write pulse/client.config: %s", err)
        else:
            _LOGGER.info("Update pulse/client.config: %s", self.path_pulse)

    async def _hardware_events(self, device: Device) -> None:
        """Process hardware requests."""
        if (
            not self.sys_hardware.policy.is_match_cgroup(PolicyGroup.UART, device)
            or not self.version
            or self.version == LANDINGPAGE
            or self.version < "2021.9.0"
        ):
            return

        configuration: (
            dict[str, Any] | None
        ) = await self.sys_homeassistant.websocket.async_send_command(
            {ATTR_TYPE: "get_config"}
        )
        if not configuration or "usb" not in configuration.get("components", []):
            return

        self.sys_homeassistant.websocket.send_message({ATTR_TYPE: "usb/scan"})

    @Job(name="home_assistant_module_begin_backup")
    async def begin_backup(self) -> None:
        """Inform Home Assistant a backup is beginning."""
        try:
            resp: dict[str, Any] | None = await self.websocket.async_send_command(
                {ATTR_TYPE: WSType.BACKUP_START}
            )
        except HomeAssistantWSError as err:
            raise HomeAssistantBackupError(
                f"Preparing backup of Home Assistant Core failed. Failed to inform HA Core: {str(err)}.",
                _LOGGER.error,
            ) from err

        if resp and not resp.get(ATTR_SUCCESS):
            raise HomeAssistantBackupError(
                f"Preparing backup of Home Assistant Core failed due to: {resp.get(ATTR_ERROR, {}).get(ATTR_MESSAGE, '')}. Check HA Core logs.",
                _LOGGER.error,
            )

    @Job(name="home_assistant_module_end_backup")
    async def end_backup(self) -> None:
        """Inform Home Assistant the backup is ending."""
        try:
            resp: dict[str, Any] | None = await self.websocket.async_send_command(
                {ATTR_TYPE: WSType.BACKUP_END}
            )
        except HomeAssistantWSError as err:
            _LOGGER.warning(
                "Error resuming normal operations after backup of Home Assistant Core. Failed to inform HA Core: %s.",
                str(err),
            )
        else:
            if resp and not resp.get(ATTR_SUCCESS):
                _LOGGER.warning(
                    "Error resuming normal operations after backup of Home Assistant Core due to: %s. Check HA Core logs.",
                    resp.get(ATTR_ERROR, {}).get(ATTR_MESSAGE, ""),
                )

    @Job(name="home_assistant_module_backup")
    async def backup(
        self, tar_file: tarfile.TarFile, exclude_database: bool = False
    ) -> None:
        """Backup Home Assistant Core config/directory."""
        excludes = HOMEASSISTANT_BACKUP_EXCLUDE.copy()
        if exclude_database:
            excludes += HOMEASSISTANT_BACKUP_EXCLUDE_DATABASE

        def _is_excluded_by_filter(path: PurePath) -> bool:
            """Filter function to filter out excluded files from the backup."""
            for exclude in excludes:
                if not path.full_match(f"data/{exclude}"):
                    continue
                _LOGGER.debug("Ignoring %s because of %s", path, exclude)
                return True

            return False

        # Backup data config folder
        def _write_tarfile(metadata: dict[str, Any]) -> None:
            """Write tarfile."""
            with TemporaryDirectory(dir=self.sys_config.path_tmp) as temp:
                temp_path = Path(temp)

                # Store local configs/state
                try:
                    write_json_file(temp_path.joinpath("homeassistant.json"), metadata)
                except ConfigurationFileError as err:
                    raise HomeAssistantError(
                        f"Can't save meta for Home Assistant Core: {err!s}",
                        _LOGGER.error,
                    ) from err

                try:
                    with tar_file as backup:
                        # Backup metadata
                        backup.add(temp, arcname=".")

                        # Backup data
                        atomic_contents_add(
                            backup,
                            self.sys_config.path_homeassistant,
                            file_filter=_is_excluded_by_filter,
                            arcname="data",
                        )
                except (tarfile.TarError, OSError, AddFileError) as err:
                    raise HomeAssistantBackupError(
                        f"Can't backup Home Assistant Core config folder: {str(err)}",
                        _LOGGER.error,
                    ) from err

        await self.begin_backup()
        try:
            _LOGGER.info("Backing up Home Assistant Core config folder")
            await self.sys_run_in_executor(_write_tarfile, self._data)
            _LOGGER.info("Backup Home Assistant Core config folder done")
        finally:
            await self.end_backup()

    @Job(name="home_assistant_module_restore")
    async def restore(
        self, tar_file: tarfile.TarFile, exclude_database: bool = False
    ) -> None:
        """Restore Home Assistant Core config/ directory."""

        def _restore_home_assistant() -> Any:
            """Restores data and reads metadata from backup.

            Returns: Home Assistant metdata
            """
            with TemporaryDirectory(dir=self.sys_config.path_tmp) as temp:
                temp_path = Path(temp)
                temp_data = temp_path.joinpath("data")
                temp_meta = temp_path.joinpath("homeassistant.json")

                # extract backup
                try:
                    with tar_file as backup:
                        backup.extractall(
                            path=temp_path,
                            members=secure_path(backup),
                            filter="fully_trusted",
                        )
                except tarfile.TarError as err:
                    raise HomeAssistantError(
                        f"Can't read tarfile {tar_file}: {err}", _LOGGER.error
                    ) from err

                # Check old backup format v1
                if not temp_data.exists():
                    temp_data = temp_path

                _LOGGER.info("Restore Home Assistant Core config folder")
                if exclude_database:
                    remove_folder_with_excludes(
                        self.sys_config.path_homeassistant,
                        excludes=HOMEASSISTANT_BACKUP_EXCLUDE_DATABASE,
                        tmp_dir=self.sys_config.path_tmp,
                    )
                else:
                    remove_folder(self.sys_config.path_homeassistant)

                try:
                    shutil.copytree(
                        temp_data,
                        self.sys_config.path_homeassistant,
                        symlinks=True,
                        dirs_exist_ok=True,
                    )
                except shutil.Error as err:
                    raise HomeAssistantError(
                        f"Can't restore origin data: {err}", _LOGGER.error
                    ) from err

                _LOGGER.info("Restore Home Assistant Core config folder done")

                if not temp_meta.exists():
                    return None
                _LOGGER.info("Restore Home Assistant Core metadata")

                # Read backup data
                try:
                    data = read_json_file(temp_meta)
                except ConfigurationFileError as err:
                    raise HomeAssistantError() from err

                return data

        data = await self.sys_run_in_executor(_restore_home_assistant)
        if data is None:
            return

        # Validate metadata
        try:
            data = SCHEMA_HASS_CONFIG(data)
        except vol.Invalid as err:
            raise HomeAssistantError(
                f"Can't validate backup data: {humanize_error(data, err)}",
                _LOGGER.error,
            ) from err

        # Restore metadata
        for attr in (
            ATTR_AUDIO_INPUT,
            ATTR_AUDIO_OUTPUT,
            ATTR_PORT,
            ATTR_SSL,
            ATTR_REFRESH_TOKEN,
            ATTR_WATCHDOG,
        ):
            if attr in data:
                self._data[attr] = data[attr]

    @Job(
        name="home_assistant_get_users",
        limit=JobExecutionLimit.THROTTLE_WAIT,
        throttle_period=timedelta(minutes=5),
        internal=True,
    )
    async def get_users(self) -> list[IngressSessionDataUser]:
        """Get list of all configured users."""
        list_of_users: (
            list[dict[str, Any]] | None
        ) = await self.sys_homeassistant.websocket.async_send_command(
            {ATTR_TYPE: "config/auth/list"}
        )

        if list_of_users:
            return [
                IngressSessionDataUser(
                    id=data["id"],
                    username=data.get("username"),
                    display_name=data.get("name"),
                )
                for data in list_of_users
            ]
        return []
