"""Representation of a backup file."""
import asyncio
from base64 import b64decode, b64encode
from collections.abc import Awaitable
from datetime import timedelta
from functools import cached_property
import json
import logging
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
from typing import Any

from awesomeversion import AwesomeVersion, AwesomeVersionCompareException
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from securetar import SecureTarFile, atomic_contents_add, secure_path
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..addons import Addon
from ..const import (
    ATTR_ADDONS,
    ATTR_COMPRESSED,
    ATTR_CRYPTO,
    ATTR_DATE,
    ATTR_DOCKER,
    ATTR_EXCLUDE_DATABASE,
    ATTR_FOLDERS,
    ATTR_HOMEASSISTANT,
    ATTR_NAME,
    ATTR_PASSWORD,
    ATTR_PROTECTED,
    ATTR_REGISTRIES,
    ATTR_REPOSITORIES,
    ATTR_SIZE,
    ATTR_SLUG,
    ATTR_SUPERVISOR_VERSION,
    ATTR_TYPE,
    ATTR_USERNAME,
    ATTR_VERSION,
    CRYPTO_AES128,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import AddonsError, BackupError
from ..utils import remove_folder
from ..utils.dt import parse_datetime, utcnow
from ..utils.json import write_json_file
from .const import BUF_SIZE, BackupType
from .utils import key_to_iv, password_to_key
from .validate import SCHEMA_BACKUP

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Backup(CoreSysAttributes):
    """A single Supervisor backup."""

    def __init__(self, coresys: CoreSys, tar_file: Path):
        """Initialize a backup."""
        self.coresys: CoreSys = coresys
        self._tarfile: Path = tar_file
        self._data: dict[str, Any] = {}
        self._tmp = None
        self._key: bytes | None = None
        self._aes: Cipher | None = None

    @property
    def version(self) -> int:
        """Return backup version."""
        return self._data[ATTR_VERSION]

    @property
    def slug(self) -> str:
        """Return backup slug."""
        return self._data[ATTR_SLUG]

    @property
    def sys_type(self) -> BackupType:
        """Return backup type."""
        return self._data[ATTR_TYPE]

    @property
    def name(self) -> str:
        """Return backup name."""
        return self._data[ATTR_NAME]

    @property
    def date(self):
        """Return backup date."""
        return self._data[ATTR_DATE]

    @property
    def protected(self) -> bool:
        """Return backup date."""
        return self._data[ATTR_PROTECTED]

    @property
    def compressed(self) -> bool:
        """Return whether backup is compressed."""
        return self._data[ATTR_COMPRESSED]

    @property
    def addons(self):
        """Return backup date."""
        return self._data[ATTR_ADDONS]

    @property
    def addon_list(self):
        """Return a list of add-ons slugs."""
        return [addon_data[ATTR_SLUG] for addon_data in self.addons]

    @property
    def folders(self):
        """Return list of saved folders."""
        return self._data[ATTR_FOLDERS]

    @property
    def repositories(self):
        """Return backup date."""
        return self._data[ATTR_REPOSITORIES]

    @repositories.setter
    def repositories(self, value):
        """Set backup date."""
        self._data[ATTR_REPOSITORIES] = value

    @property
    def homeassistant_version(self):
        """Return backup Home Assistant version."""
        if self.homeassistant is None:
            return None
        return self.homeassistant[ATTR_VERSION]

    @property
    def homeassistant_exclude_database(self) -> bool:
        """Return whether database was excluded from Home Assistant backup."""
        if self.homeassistant is None:
            return None
        return self.homeassistant[ATTR_EXCLUDE_DATABASE]

    @property
    def homeassistant(self):
        """Return backup Home Assistant data."""
        return self._data[ATTR_HOMEASSISTANT]

    @property
    def supervisor_version(self) -> AwesomeVersion:
        """Return backup Supervisor version."""
        return self._data[ATTR_SUPERVISOR_VERSION]

    @property
    def docker(self):
        """Return backup Docker config data."""
        return self._data.get(ATTR_DOCKER, {})

    @docker.setter
    def docker(self, value):
        """Set the Docker config data."""
        self._data[ATTR_DOCKER] = value

    @cached_property
    def location(self) -> str | None:
        """Return the location of the backup."""
        for backup_mount in self.sys_mounts.backup_mounts:
            if self.tarfile.is_relative_to(backup_mount.local_where):
                return backup_mount.name
        return None

    @property
    def size(self):
        """Return backup size."""
        if not self.tarfile.is_file():
            return 0
        return round(self.tarfile.stat().st_size / 1048576, 2)  # calc mbyte

    @property
    def is_new(self):
        """Return True if there is new."""
        return not self.tarfile.exists()

    @property
    def tarfile(self):
        """Return path to backup tarfile."""
        return self._tarfile

    @property
    def is_current(self):
        """Return true if backup is current, false if stale."""
        return parse_datetime(self.date) >= utcnow() - timedelta(
            days=self.sys_backups.days_until_stale
        )

    def new(
        self,
        slug: str,
        name: str,
        date: str,
        sys_type: BackupType,
        password: str | None = None,
        compressed: bool = True,
    ):
        """Initialize a new backup."""
        # Init metadata
        self._data[ATTR_VERSION] = 2
        self._data[ATTR_SLUG] = slug
        self._data[ATTR_NAME] = name
        self._data[ATTR_DATE] = date
        self._data[ATTR_TYPE] = sys_type
        self._data[ATTR_SUPERVISOR_VERSION] = self.sys_supervisor.version

        # Add defaults
        self._data = SCHEMA_BACKUP(self._data)

        # Set password
        if password:
            self._init_password(password)
            self._data[ATTR_PROTECTED] = True
            self._data[ATTR_CRYPTO] = CRYPTO_AES128

        if not compressed:
            self._data[ATTR_COMPRESSED] = False

    def set_password(self, password: str) -> bool:
        """Set the password for an existing backup."""
        if not password:
            return False
        self._init_password(password)
        return True

    def _init_password(self, password: str) -> None:
        """Set password + init aes cipher."""
        self._key = password_to_key(password)
        self._aes = Cipher(
            algorithms.AES(self._key),
            modes.CBC(key_to_iv(self._key)),
            backend=default_backend(),
        )

    def _encrypt_data(self, data: str) -> str:
        """Make data secure."""
        if not self._key or data is None:
            return data

        encrypt = self._aes.encryptor()
        padder = padding.PKCS7(128).padder()

        data = padder.update(data.encode()) + padder.finalize()
        return b64encode(encrypt.update(data)).decode()

    def _decrypt_data(self, data: str) -> str:
        """Make data readable."""
        if not self._key or data is None:
            return data

        decrypt = self._aes.decryptor()
        padder = padding.PKCS7(128).unpadder()

        data = padder.update(decrypt.update(b64decode(data))) + padder.finalize()
        return data.decode()

    async def load(self):
        """Read backup.json from tar file."""
        if not self.tarfile.is_file():
            _LOGGER.error("No tarfile located at %s", self.tarfile)
            return False

        def _load_file():
            """Read backup.json."""
            with tarfile.open(self.tarfile, "r:") as backup:
                if "./snapshot.json" in [entry.name for entry in backup.getmembers()]:
                    # Old backups stil uses "snapshot.json", we need to support that forever
                    json_file = backup.extractfile("./snapshot.json")
                else:
                    json_file = backup.extractfile("./backup.json")
                return json_file.read()

        # read backup.json
        try:
            raw = await self.sys_run_in_executor(_load_file)
        except (tarfile.TarError, KeyError) as err:
            _LOGGER.error("Can't read backup tarfile %s: %s", self.tarfile, err)
            return False

        # parse data
        try:
            raw_dict = json.loads(raw)
        except json.JSONDecodeError as err:
            _LOGGER.error("Can't read data for %s: %s", self.tarfile, err)
            return False

        # validate
        try:
            self._data = SCHEMA_BACKUP(raw_dict)
        except vol.Invalid as err:
            _LOGGER.error(
                "Can't validate data for %s: %s",
                self.tarfile,
                humanize_error(raw_dict, err),
            )
            return False

        return True

    async def __aenter__(self):
        """Async context to open a backup."""
        self._tmp = TemporaryDirectory(dir=str(self.tarfile.parent))

        # create a backup
        if not self.tarfile.is_file():
            return self

        # extract an existing backup
        def _extract_backup():
            """Extract a backup."""
            with tarfile.open(self.tarfile, "r:") as tar:
                tar.extractall(path=self._tmp.name, members=secure_path(tar))

        await self.sys_run_in_executor(_extract_backup)

    async def __aexit__(self, exception_type, exception_value, traceback):
        """Async context to close a backup."""
        # exists backup or exception on build
        if self.tarfile.is_file() or exception_type is not None:
            self._tmp.cleanup()
            return

        # validate data
        try:
            self._data = SCHEMA_BACKUP(self._data)
        except vol.Invalid as err:
            _LOGGER.error(
                "Invalid data for %s: %s", self.tarfile, humanize_error(self._data, err)
            )
            raise ValueError("Invalid config") from None

        # new backup, build it
        def _create_backup():
            """Create a new backup."""
            with tarfile.open(self.tarfile, "w:") as tar:
                tar.add(self._tmp.name, arcname=".")

        try:
            write_json_file(Path(self._tmp.name, "backup.json"), self._data)
            await self.sys_run_in_executor(_create_backup)
        except (OSError, json.JSONDecodeError) as err:
            _LOGGER.error("Can't write backup: %s", err)
        finally:
            self._tmp.cleanup()

    async def store_addons(self, addon_list: list[str]) -> list[asyncio.Task]:
        """Add a list of add-ons into backup.

        For each addon that needs to be started after backup, returns a Task which
        completes when that addon has state 'started' (see addon.start).
        """

        async def _addon_save(addon: Addon) -> asyncio.Task | None:
            """Task to store an add-on into backup."""
            tar_name = f"{addon.slug}.tar{'.gz' if self.compressed else ''}"
            addon_file = SecureTarFile(
                Path(self._tmp.name, tar_name),
                "w",
                key=self._key,
                gzip=self.compressed,
                bufsize=BUF_SIZE,
            )

            # Take backup
            try:
                start_task = await addon.backup(addon_file)
            except AddonsError:
                _LOGGER.error("Can't create backup for %s", addon.slug)
                return

            # Store to config
            self._data[ATTR_ADDONS].append(
                {
                    ATTR_SLUG: addon.slug,
                    ATTR_NAME: addon.name,
                    ATTR_VERSION: addon.version,
                    ATTR_SIZE: addon_file.size,
                }
            )

            return start_task

        # Save Add-ons sequential
        # avoid issue on slow IO
        start_tasks: list[asyncio.Task] = []
        for addon in addon_list:
            try:
                if start_task := await _addon_save(addon):
                    start_tasks.append(start_task)
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't save Add-on %s: %s", addon.slug, err)

        return start_tasks

    async def restore_addons(self, addon_list: list[str]) -> list[asyncio.Task]:
        """Restore a list add-on from backup."""

        async def _addon_restore(addon_slug: str) -> asyncio.Task | None:
            """Task to restore an add-on into backup."""
            tar_name = f"{addon_slug}.tar{'.gz' if self.compressed else ''}"
            addon_file = SecureTarFile(
                Path(self._tmp.name, tar_name),
                "r",
                key=self._key,
                gzip=self.compressed,
                bufsize=BUF_SIZE,
            )

            # If exists inside backup
            if not addon_file.path.exists():
                _LOGGER.error("Can't find backup %s", addon_slug)
                return

            # Perform a restore
            try:
                return await self.sys_addons.restore(addon_slug, addon_file)
            except AddonsError:
                _LOGGER.error("Can't restore backup %s", addon_slug)

        # Save Add-ons sequential
        # avoid issue on slow IO
        start_tasks: list[asyncio.Task] = []
        for slug in addon_list:
            try:
                if start_task := await _addon_restore(slug):
                    start_tasks.append(start_task)
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't restore Add-on %s: %s", slug, err)

        return start_tasks

    async def store_folders(self, folder_list: list[str]):
        """Backup Supervisor data into backup."""

        async def _folder_save(name: str):
            """Take backup of a folder."""
            slug_name = name.replace("/", "_")
            tar_name = Path(
                self._tmp.name, f"{slug_name}.tar{'.gz' if self.compressed else ''}"
            )
            origin_dir = Path(self.sys_config.path_supervisor, name)

            # Check if exists
            if not origin_dir.is_dir():
                _LOGGER.warning("Can't find backup folder %s", name)
                return

            def _save() -> None:
                # Take backup
                _LOGGER.info("Backing up folder %s", name)
                with SecureTarFile(
                    tar_name, "w", key=self._key, gzip=self.compressed, bufsize=BUF_SIZE
                ) as tar_file:
                    atomic_contents_add(
                        tar_file,
                        origin_dir,
                        excludes=[
                            bound.bind_mount.local_where.as_posix()
                            for bound in self.sys_mounts.bound_mounts
                            if bound.bind_mount.local_where
                        ],
                        arcname=".",
                    )

                _LOGGER.info("Backup folder %s done", name)

            await self.sys_run_in_executor(_save)
            self._data[ATTR_FOLDERS].append(name)

        # Save folder sequential
        # avoid issue on slow IO
        for folder in folder_list:
            try:
                await _folder_save(folder)
            except (tarfile.TarError, OSError) as err:
                raise BackupError(
                    f"Can't backup folder {folder}: {str(err)}", _LOGGER.error
                ) from err

    async def restore_folders(self, folder_list: list[str]):
        """Backup Supervisor data into backup."""

        async def _folder_restore(name: str) -> None:
            """Intenal function to restore a folder."""
            slug_name = name.replace("/", "_")
            tar_name = Path(
                self._tmp.name, f"{slug_name}.tar{'.gz' if self.compressed else ''}"
            )
            origin_dir = Path(self.sys_config.path_supervisor, name)

            # Check if exists inside backup
            if not tar_name.exists():
                _LOGGER.warning("Can't find restore folder %s", name)
                return

            # Unmount any mounts within folder
            bind_mounts = [
                bound.bind_mount
                for bound in self.sys_mounts.bound_mounts
                if bound.bind_mount.local_where
                and bound.bind_mount.local_where.is_relative_to(origin_dir)
            ]
            if bind_mounts:
                await asyncio.gather(
                    *[bind_mount.unmount() for bind_mount in bind_mounts]
                )

            # Clean old stuff
            if origin_dir.is_dir():
                await remove_folder(origin_dir, content_only=True)

            # Perform a restore
            def _restore() -> None:
                try:
                    _LOGGER.info("Restore folder %s", name)
                    with SecureTarFile(
                        tar_name,
                        "r",
                        key=self._key,
                        gzip=self.compressed,
                        bufsize=BUF_SIZE,
                    ) as tar_file:
                        tar_file.extractall(path=origin_dir, members=tar_file)
                    _LOGGER.info("Restore folder %s done", name)
                except (tarfile.TarError, OSError) as err:
                    _LOGGER.warning("Can't restore folder %s: %s", name, err)

            try:
                await self.sys_run_in_executor(_restore)
            finally:
                if bind_mounts:
                    await asyncio.gather(
                        *[bind_mount.mount() for bind_mount in bind_mounts]
                    )

        # Restore folder sequential
        # avoid issue on slow IO
        for folder in folder_list:
            try:
                await _folder_restore(folder)
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't restore folder %s: %s", folder, err)

    async def store_homeassistant(self, exclude_database: bool = False):
        """Backup Home Assistant Core configuration folder."""
        self._data[ATTR_HOMEASSISTANT] = {
            ATTR_VERSION: self.sys_homeassistant.version,
            ATTR_EXCLUDE_DATABASE: exclude_database,
        }

        # Backup Home Assistant Core config directory
        tar_name = Path(
            self._tmp.name, f"homeassistant.tar{'.gz' if self.compressed else ''}"
        )
        homeassistant_file = SecureTarFile(
            tar_name, "w", key=self._key, gzip=self.compressed, bufsize=BUF_SIZE
        )

        await self.sys_homeassistant.backup(homeassistant_file, exclude_database)

        # Store size
        self.homeassistant[ATTR_SIZE] = homeassistant_file.size

    async def restore_homeassistant(self) -> Awaitable[None]:
        """Restore Home Assistant Core configuration folder."""
        await self.sys_homeassistant.core.stop()

        # Restore Home Assistant Core config directory
        tar_name = Path(
            self._tmp.name, f"homeassistant.tar{'.gz' if self.compressed else ''}"
        )
        homeassistant_file = SecureTarFile(
            tar_name, "r", key=self._key, gzip=self.compressed, bufsize=BUF_SIZE
        )

        await self.sys_homeassistant.restore(
            homeassistant_file, self.homeassistant_exclude_database
        )

        # Generate restore task
        async def _core_update():
            try:
                if self.homeassistant_version == self.sys_homeassistant.version:
                    return
            except TypeError:
                # Home Assistant is not yet installed / None
                pass
            except AwesomeVersionCompareException as err:
                raise BackupError(
                    f"Invalid Home Assistant Core version {self.homeassistant_version}",
                    _LOGGER.error,
                ) from err
            await self.sys_homeassistant.core.update(self.homeassistant_version)

        return self.sys_create_task(_core_update())

    def store_repositories(self):
        """Store repository list into backup."""
        self.repositories = self.sys_store.repository_urls

    async def restore_repositories(self, replace: bool = False):
        """Restore repositories from backup.

        Return a coroutine.
        """
        await self.sys_store.update_repositories(
            self.repositories, add_with_errors=True, replace=replace
        )

    def store_dockerconfig(self):
        """Store the configuration for Docker."""
        self.docker = {
            ATTR_REGISTRIES: {
                registry: {
                    ATTR_USERNAME: credentials[ATTR_USERNAME],
                    ATTR_PASSWORD: self._encrypt_data(credentials[ATTR_PASSWORD]),
                }
                for registry, credentials in self.sys_docker.config.registries.items()
            }
        }

    def restore_dockerconfig(self, replace: bool = False):
        """Restore the configuration for Docker."""
        if replace:
            self.sys_docker.config.registries.clear()

        if ATTR_REGISTRIES in self.docker:
            self.sys_docker.config.registries.update(
                {
                    registry: {
                        ATTR_USERNAME: credentials[ATTR_USERNAME],
                        ATTR_PASSWORD: self._decrypt_data(credentials[ATTR_PASSWORD]),
                    }
                    for registry, credentials in self.docker[ATTR_REGISTRIES].items()
                }
            )
            self.sys_docker.config.save_data()
