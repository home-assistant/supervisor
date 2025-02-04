"""Representation of a backup file."""

import asyncio
from base64 import b64decode, b64encode
from collections import defaultdict
from collections.abc import AsyncGenerator, Awaitable
from contextlib import asynccontextmanager
from copy import deepcopy
from datetime import timedelta
from functools import lru_cache
import io
import json
import logging
from pathlib import Path, PurePath
import tarfile
from tarfile import TarFile
from tempfile import TemporaryDirectory
import time
from typing import Any, Self

from awesomeversion import AwesomeVersion, AwesomeVersionCompareException
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from securetar import SecureTarFile, atomic_contents_add, secure_path
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..addons.manager import Addon
from ..const import (
    ATTR_ADDONS,
    ATTR_COMPRESSED,
    ATTR_CRYPTO,
    ATTR_DATE,
    ATTR_DOCKER,
    ATTR_EXCLUDE_DATABASE,
    ATTR_EXTRA,
    ATTR_FOLDERS,
    ATTR_HOMEASSISTANT,
    ATTR_NAME,
    ATTR_PASSWORD,
    ATTR_PATH,
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
from ..coresys import CoreSys
from ..exceptions import (
    AddonsError,
    BackupError,
    BackupFileNotFoundError,
    BackupInvalidError,
)
from ..jobs.const import JOB_GROUP_BACKUP
from ..jobs.decorator import Job
from ..jobs.job_group import JobGroup
from ..utils import remove_folder
from ..utils.dt import parse_datetime, utcnow
from ..utils.json import json_bytes
from ..utils.sentinel import DEFAULT
from .const import BUF_SIZE, LOCATION_CLOUD_BACKUP, BackupType
from .utils import key_to_iv, password_to_key
from .validate import SCHEMA_BACKUP

_LOGGER: logging.Logger = logging.getLogger(__name__)


@lru_cache
def _backup_file_size(backup: Path) -> int:
    """Get backup file size."""
    return backup.stat().st_size if backup.is_file() else 0


def location_sort_key(value: str | None) -> str:
    """Sort locations, None is always first else alphabetical."""
    return value if value else ""


class Backup(JobGroup):
    """A single Supervisor backup."""

    def __init__(
        self,
        coresys: CoreSys,
        tar_file: Path,
        slug: str,
        location: str | None,
        data: dict[str, Any] | None = None,
    ):
        """Initialize a backup."""
        super().__init__(
            coresys, JOB_GROUP_BACKUP.format_map(defaultdict(str, slug=slug)), slug
        )
        self._data: dict[str, Any] = data or {ATTR_SLUG: slug}
        self._tmp = None
        self._outer_secure_tarfile: SecureTarFile | None = None
        self._key: bytes | None = None
        self._aes: Cipher | None = None
        self._locations: dict[str | None, dict[str, Path | bool]] = {
            location: {
                ATTR_PATH: tar_file,
                ATTR_PROTECTED: data.get(ATTR_PROTECTED, False) if data else False,
            }
        }

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
    def date(self) -> str:
        """Return backup date."""
        return self._data[ATTR_DATE]

    @property
    def protected(self) -> bool:
        """Return backup date."""
        return self._locations[self.location][ATTR_PROTECTED]

    @property
    def compressed(self) -> bool:
        """Return whether backup is compressed."""
        return self._data[ATTR_COMPRESSED]

    @property
    def addons(self) -> list[dict[str, Any]]:
        """Return backup date."""
        return self._data[ATTR_ADDONS]

    @property
    def addon_list(self) -> list[str]:
        """Return a list of add-ons slugs."""
        return [addon_data[ATTR_SLUG] for addon_data in self.addons]

    @property
    def folders(self) -> list[str]:
        """Return list of saved folders."""
        return self._data[ATTR_FOLDERS]

    @property
    def repositories(self) -> list[str]:
        """Return add-on store repositories."""
        return self._data[ATTR_REPOSITORIES]

    @repositories.setter
    def repositories(self, value: list[str]) -> None:
        """Set add-on store repositories."""
        self._data[ATTR_REPOSITORIES] = value

    @property
    def homeassistant_version(self) -> AwesomeVersion:
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
    def homeassistant(self) -> dict[str, Any]:
        """Return backup Home Assistant data."""
        return self._data[ATTR_HOMEASSISTANT]

    @property
    def supervisor_version(self) -> AwesomeVersion:
        """Return backup Supervisor version."""
        return self._data[ATTR_SUPERVISOR_VERSION]

    @property
    def extra(self) -> dict:
        """Get extra metadata added by client."""
        return self._data[ATTR_EXTRA]

    @property
    def docker(self) -> dict[str, Any]:
        """Return backup Docker config data."""
        return self._data.get(ATTR_DOCKER, {})

    @docker.setter
    def docker(self, value: dict[str, Any]) -> None:
        """Set the Docker config data."""
        self._data[ATTR_DOCKER] = value

    @property
    def location(self) -> str | None:
        """Return the location of the backup."""
        return self.locations[0]

    @property
    def all_locations(self) -> dict[str | None, dict[str, Path | bool]]:
        """Return all locations this backup was found in."""
        return self._locations

    @property
    def locations(self) -> list[str | None]:
        """Return locations this backup was found in except cloud backup (unless that's the only one)."""
        if len(self._locations) == 1:
            return list(self._locations)
        return sorted(
            [
                location
                for location in self._locations
                if location != LOCATION_CLOUD_BACKUP
            ],
            key=location_sort_key,
        )

    @property
    def size(self) -> float:
        """Return backup size."""
        return round(self.size_bytes / 1048576, 2)  # calc mbyte

    @property
    def size_bytes(self) -> int:
        """Return backup size in bytes."""
        return self.location_size(self.location)

    @property
    def is_new(self) -> bool:
        """Return True if there is new."""
        return not self.tarfile.exists()

    @property
    def tarfile(self) -> Path:
        """Return path to backup tarfile."""
        return self._locations[self.location][ATTR_PATH]

    @property
    def is_current(self) -> bool:
        """Return true if backup is current, false if stale."""
        return parse_datetime(self.date) >= utcnow() - timedelta(
            days=self.sys_backups.days_until_stale
        )

    @property
    def data(self) -> dict[str, Any]:
        """Returns a copy of the data."""
        return deepcopy(self._data)

    def location_size(self, location: str | None) -> int:
        """Get size of backup in a location."""
        if location not in self.all_locations:
            return 0

        backup = self.all_locations[location][ATTR_PATH]
        return _backup_file_size(backup)

    def __eq__(self, other: Any) -> bool:
        """Return true if backups have same metadata."""
        if not isinstance(other, Backup):
            return False

        # Compare all fields except ones about protection. Current encryption status does not affect equality
        keys = self._data.keys() | other._data.keys()
        for k in keys - {ATTR_PROTECTED, ATTR_CRYPTO, ATTR_DOCKER}:
            if (
                k not in self._data
                or k not in other._data
                or self._data[k] != other._data[k]
            ):
                _LOGGER.info(
                    "Backup %s and %s not equal because %s field has different value: %s and %s",
                    self.slug,
                    other.slug,
                    k,
                    self._data.get(k),
                    other._data.get(k),
                )
                return False
        return True

    def consolidate(self, backup: Self) -> None:
        """Consolidate two backups with same slug in different locations."""
        if self.slug != backup.slug:
            raise ValueError(
                f"Backup {self.slug} and {backup.slug} are not the same backup"
            )
        if self != backup:
            raise BackupInvalidError(
                f"Backup in {backup.location} and {self.location} both have slug {self.slug} but are not the same!"
            )

        # In case of conflict we always ignore the ones from the first one. But log them to let the user know

        if conflict := {
            loc: val[ATTR_PATH]
            for loc, val in self.all_locations.items()
            if loc in backup.all_locations and backup.all_locations[loc] != val
        }:
            _LOGGER.warning(
                "Backup %s exists in two files in locations %s. Ignoring %s",
                self.slug,
                ", ".join(str(loc) for loc in conflict),
                ", ".join([path.as_posix() for path in conflict.values()]),
            )
        self._locations.update(backup.all_locations)

    def new(
        self,
        name: str,
        date: str,
        sys_type: BackupType,
        password: str | None = None,
        compressed: bool = True,
        extra: dict | None = None,
    ):
        """Initialize a new backup."""
        # Init metadata
        self._data[ATTR_VERSION] = 2
        self._data[ATTR_NAME] = name
        self._data[ATTR_DATE] = date
        self._data[ATTR_TYPE] = sys_type
        self._data[ATTR_SUPERVISOR_VERSION] = self.sys_supervisor.version
        self._data[ATTR_EXTRA] = extra or {}

        # Add defaults
        self._data = SCHEMA_BACKUP(self._data)

        # Set password
        if password:
            self._init_password(password)
            self._data[ATTR_PROTECTED] = True
            self._data[ATTR_CRYPTO] = CRYPTO_AES128
            self._locations[self.location][ATTR_PROTECTED] = True

        if not compressed:
            self._data[ATTR_COMPRESSED] = False

    def set_password(self, password: str | None) -> None:
        """Set the password for an existing backup."""
        if password:
            self._init_password(password)
        else:
            self._key = None
            self._aes = None

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

    async def validate_password(self, location: str | None) -> bool:
        """Validate backup password.

        Returns false only when the password is known to be wrong.
        """
        backup_file: Path = self.all_locations[location][ATTR_PATH]

        def _validate_file() -> bool:
            ending = f".tar{'.gz' if self.compressed else ''}"

            with tarfile.open(backup_file, "r:") as backup:
                test_tar_name = next(
                    (
                        entry.name
                        for entry in backup.getmembers()
                        if entry.name.endswith(ending)
                    ),
                    None,
                )
                if not test_tar_name:
                    _LOGGER.warning("No tar file found to validate password with")
                    return True

                test_tar_file = backup.extractfile(test_tar_name)
                try:
                    with SecureTarFile(
                        ending,  # Not used
                        gzip=self.compressed,
                        key=self._key,
                        mode="r",
                        fileobj=test_tar_file,
                    ):
                        # If we can read the tar file, the password is correct
                        return True
                except tarfile.ReadError:
                    _LOGGER.debug("Invalid password")
                    return False
                except Exception:  # pylint: disable=broad-exception-caught
                    _LOGGER.exception("Unexpected error validating password")
                    return True

        try:
            return await self.sys_run_in_executor(_validate_file)
        except FileNotFoundError as err:
            self.sys_create_task(self.sys_backups.reload(location))
            raise BackupFileNotFoundError(
                f"Cannot validate backup at {backup_file.as_posix()}, file does not exist!",
                _LOGGER.error,
            ) from err

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

        if self._data[ATTR_PROTECTED]:
            self._locations[self.location][ATTR_PROTECTED] = True

        return True

    @asynccontextmanager
    async def create(self) -> AsyncGenerator[None]:
        """Create new backup file."""
        if self.tarfile.is_file():
            raise BackupError(
                f"Cannot make new backup at {self.tarfile.as_posix()}, file already exists!",
                _LOGGER.error,
            )

        self._outer_secure_tarfile = SecureTarFile(
            self.tarfile,
            "w",
            gzip=False,
            bufsize=BUF_SIZE,
        )
        try:
            with self._outer_secure_tarfile as outer_tarfile:
                yield
                await self._create_cleanup(outer_tarfile)
        finally:
            self._outer_secure_tarfile = None

    @asynccontextmanager
    async def open(self, location: str | None | type[DEFAULT]) -> AsyncGenerator[None]:
        """Open backup for restore."""
        if location != DEFAULT and location not in self.all_locations:
            raise BackupError(
                f"Backup {self.slug} does not exist in location {location}",
                _LOGGER.error,
            )

        backup_tarfile = (
            self.tarfile
            if location == DEFAULT
            else self.all_locations[location][ATTR_PATH]
        )
        if not backup_tarfile.is_file():
            self.sys_create_task(self.sys_backups.reload(location))
            raise BackupFileNotFoundError(
                f"Cannot open backup at {backup_tarfile.as_posix()}, file does not exist!",
                _LOGGER.error,
            )

        # extract an existing backup
        self._tmp = TemporaryDirectory(dir=str(backup_tarfile.parent))

        def _extract_backup():
            """Extract a backup."""
            with tarfile.open(backup_tarfile, "r:") as tar:
                tar.extractall(
                    path=self._tmp.name,
                    members=secure_path(tar),
                    filter="fully_trusted",
                )

        with self._tmp:
            await self.sys_run_in_executor(_extract_backup)
            yield

    async def _create_cleanup(self, outer_tarfile: TarFile) -> None:
        """Cleanup after backup creation.

        Separate method to be called from create to ensure
        that cleanup is always performed, even if an exception is raised.
        """
        # validate data
        try:
            self._data = SCHEMA_BACKUP(self._data)
        except vol.Invalid as err:
            _LOGGER.error(
                "Invalid data for %s: %s", self.tarfile, humanize_error(self._data, err)
            )
            raise ValueError("Invalid config") from None

        # new backup, build it
        def _add_backup_json():
            """Create a new backup."""
            raw_bytes = json_bytes(self._data)
            fileobj = io.BytesIO(raw_bytes)
            tar_info = tarfile.TarInfo(name="./backup.json")
            tar_info.size = len(raw_bytes)
            tar_info.mtime = int(time.time())
            outer_tarfile.addfile(tar_info, fileobj=fileobj)

        try:
            await self.sys_run_in_executor(_add_backup_json)
        except (OSError, json.JSONDecodeError) as err:
            self.sys_jobs.current.capture_error(BackupError("Can't write backup"))
            _LOGGER.error("Can't write backup: %s", err)

    @Job(name="backup_addon_save", cleanup=False)
    async def _addon_save(self, addon: Addon) -> asyncio.Task | None:
        """Store an add-on into backup."""
        self.sys_jobs.current.reference = addon.slug

        tar_name = f"{addon.slug}.tar{'.gz' if self.compressed else ''}"

        addon_file = self._outer_secure_tarfile.create_inner_tar(
            f"./{tar_name}",
            gzip=self.compressed,
            key=self._key,
        )
        # Take backup
        try:
            start_task = await addon.backup(addon_file)
        except AddonsError as err:
            raise BackupError(
                f"Can't create backup for {addon.slug}", _LOGGER.error
            ) from err

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

    @Job(name="backup_store_addons", cleanup=False)
    async def store_addons(self, addon_list: list[str]) -> list[asyncio.Task]:
        """Add a list of add-ons into backup.

        For each addon that needs to be started after backup, returns a Task which
        completes when that addon has state 'started' (see addon.start).
        """
        # Save Add-ons sequential avoid issue on slow IO
        start_tasks: list[asyncio.Task] = []
        for addon in addon_list:
            try:
                if start_task := await self._addon_save(addon):
                    start_tasks.append(start_task)
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't save Add-on %s: %s", addon.slug, err)

        return start_tasks

    @Job(name="backup_addon_restore", cleanup=False)
    async def _addon_restore(self, addon_slug: str) -> asyncio.Task | None:
        """Restore an add-on from backup."""
        self.sys_jobs.current.reference = addon_slug

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
            raise BackupError(f"Can't find backup {addon_slug}", _LOGGER.error)

        # Perform a restore
        try:
            return await self.sys_addons.restore(addon_slug, addon_file)
        except AddonsError as err:
            raise BackupError(
                f"Can't restore backup {addon_slug}", _LOGGER.error
            ) from err

    @Job(name="backup_restore_addons", cleanup=False)
    async def restore_addons(
        self, addon_list: list[str]
    ) -> tuple[bool, list[asyncio.Task]]:
        """Restore a list add-on from backup."""
        # Save Add-ons sequential avoid issue on slow IO
        start_tasks: list[asyncio.Task] = []
        success = True
        for slug in addon_list:
            try:
                start_task = await self._addon_restore(slug)
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't restore Add-on %s: %s", slug, err)
                success = False
            else:
                if start_task:
                    start_tasks.append(start_task)

        return (success, start_tasks)

    @Job(name="backup_remove_delta_addons", cleanup=False)
    async def remove_delta_addons(self) -> bool:
        """Remove addons which are not in this backup."""
        success = True
        for addon in self.sys_addons.installed:
            if addon.slug in self.addon_list:
                continue

            # Remove Add-on because it's not a part of the new env
            # Do it sequential avoid issue on slow IO
            try:
                await self.sys_addons.uninstall(addon.slug)
            except AddonsError as err:
                self.sys_jobs.current.capture_error(err)
                _LOGGER.warning("Can't uninstall Add-on %s: %s", addon.slug, err)
                success = False

        return success

    @Job(name="backup_folder_save", cleanup=False)
    async def _folder_save(self, name: str):
        """Take backup of a folder."""
        self.sys_jobs.current.reference = name

        slug_name = name.replace("/", "_")
        tar_name = f"{slug_name}.tar{'.gz' if self.compressed else ''}"
        origin_dir = Path(self.sys_config.path_supervisor, name)

        # Check if exists
        if not origin_dir.is_dir():
            _LOGGER.warning("Can't find backup folder %s", name)
            return

        def _save() -> None:
            # Take backup
            _LOGGER.info("Backing up folder %s", name)

            def is_excluded_by_filter(item_arcpath: PurePath) -> bool:
                """Filter out bind mounts in folders being backed up."""
                full_path = origin_dir / item_arcpath.relative_to(".")

                for bound in self.sys_mounts.bound_mounts:
                    if full_path != bound.bind_mount.local_where:
                        continue
                    _LOGGER.debug(
                        "Ignoring %s because of %s",
                        full_path,
                        bound.bind_mount.local_where.as_posix(),
                    )
                    return True

                return False

            with self._outer_secure_tarfile.create_inner_tar(
                f"./{tar_name}",
                gzip=self.compressed,
                key=self._key,
            ) as tar_file:
                atomic_contents_add(
                    tar_file,
                    origin_dir,
                    file_filter=is_excluded_by_filter,
                    arcname=".",
                )

            _LOGGER.info("Backup folder %s done", name)

        try:
            await self.sys_run_in_executor(_save)
        except (tarfile.TarError, OSError) as err:
            raise BackupError(
                f"Can't backup folder {name}: {str(err)}", _LOGGER.error
            ) from err

        self._data[ATTR_FOLDERS].append(name)

    @Job(name="backup_store_folders", cleanup=False)
    async def store_folders(self, folder_list: list[str]):
        """Backup Supervisor data into backup."""
        # Save folder sequential avoid issue on slow IO
        for folder in folder_list:
            await self._folder_save(folder)

    @Job(name="backup_folder_restore", cleanup=False)
    async def _folder_restore(self, name: str) -> None:
        """Restore a folder."""
        self.sys_jobs.current.reference = name

        slug_name = name.replace("/", "_")
        tar_name = Path(
            self._tmp.name, f"{slug_name}.tar{'.gz' if self.compressed else ''}"
        )
        origin_dir = Path(self.sys_config.path_supervisor, name)

        # Check if exists inside backup
        if not tar_name.exists():
            raise BackupInvalidError(
                f"Can't find restore folder {name}", _LOGGER.warning
            )

        # Unmount any mounts within folder
        bind_mounts = [
            bound.bind_mount
            for bound in self.sys_mounts.bound_mounts
            if bound.bind_mount.local_where
            and bound.bind_mount.local_where.is_relative_to(origin_dir)
        ]
        if bind_mounts:
            await asyncio.gather(*[bind_mount.unmount() for bind_mount in bind_mounts])

        # Clean old stuff
        if origin_dir.is_dir():
            await remove_folder(origin_dir, content_only=True)

        # Perform a restore
        def _restore() -> bool:
            try:
                _LOGGER.info("Restore folder %s", name)
                with SecureTarFile(
                    tar_name,
                    "r",
                    key=self._key,
                    gzip=self.compressed,
                    bufsize=BUF_SIZE,
                ) as tar_file:
                    tar_file.extractall(
                        path=origin_dir, members=tar_file, filter="fully_trusted"
                    )
                _LOGGER.info("Restore folder %s done", name)
            except (tarfile.TarError, OSError) as err:
                raise BackupError(
                    f"Can't restore folder {name}: {err}", _LOGGER.warning
                ) from err
            return True

        try:
            return await self.sys_run_in_executor(_restore)
        finally:
            if bind_mounts:
                await asyncio.gather(
                    *[bind_mount.mount() for bind_mount in bind_mounts]
                )

    @Job(name="backup_restore_folders", cleanup=False)
    async def restore_folders(self, folder_list: list[str]) -> bool:
        """Backup Supervisor data into backup."""
        success = True

        # Restore folder sequential avoid issue on slow IO
        for folder in folder_list:
            try:
                await self._folder_restore(folder)
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't restore folder %s: %s", folder, err)
                success = False
        return success

    @Job(name="backup_store_homeassistant", cleanup=False)
    async def store_homeassistant(self, exclude_database: bool = False):
        """Backup Home Assistant Core configuration folder."""
        self._data[ATTR_HOMEASSISTANT] = {
            ATTR_VERSION: self.sys_homeassistant.version,
            ATTR_EXCLUDE_DATABASE: exclude_database,
        }

        tar_name = f"homeassistant.tar{'.gz' if self.compressed else ''}"
        # Backup Home Assistant Core config directory
        homeassistant_file = self._outer_secure_tarfile.create_inner_tar(
            f"./{tar_name}",
            gzip=self.compressed,
            key=self._key,
        )

        await self.sys_homeassistant.backup(homeassistant_file, exclude_database)

        # Store size
        self.homeassistant[ATTR_SIZE] = homeassistant_file.size

    @Job(name="backup_restore_homeassistant", cleanup=False)
    async def restore_homeassistant(self) -> Awaitable[None]:
        """Restore Home Assistant Core configuration folder."""
        await self.sys_homeassistant.core.stop(remove_container=True)

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

    def store_repositories(self) -> None:
        """Store repository list into backup."""
        self.repositories = self.sys_store.repository_urls

    def restore_repositories(self, replace: bool = False) -> Awaitable[None]:
        """Restore repositories from backup.

        Return a coroutine.
        """
        return self.sys_store.update_repositories(
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
