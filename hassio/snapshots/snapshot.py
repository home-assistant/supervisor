"""Representation of a snapshot file."""
import asyncio
from base64 import b64decode, b64encode
import json
import logging
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
from typing import Any, Dict, Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..const import (
    ATTR_ADDONS,
    ATTR_BOOT,
    ATTR_CRYPTO,
    ATTR_DATE,
    ATTR_FOLDERS,
    ATTR_HOMEASSISTANT,
    ATTR_IMAGE,
    ATTR_LAST_VERSION,
    ATTR_NAME,
    ATTR_PASSWORD,
    ATTR_PORT,
    ATTR_PROTECTED,
    ATTR_REFRESH_TOKEN,
    ATTR_REPOSITORIES,
    ATTR_SIZE,
    ATTR_SLUG,
    ATTR_SSL,
    ATTR_TYPE,
    ATTR_VERSION,
    ATTR_WAIT_BOOT,
    ATTR_WATCHDOG,
    CRYPTO_AES128,
    FOLDER_HOMEASSISTANT,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import AddonsError
from ..utils.json import write_json_file
from ..utils.tar import SecureTarFile, exclude_filter, secure_path
from .utils import key_to_iv, password_for_validating, password_to_key, remove_folder
from .validate import ALL_FOLDERS, SCHEMA_SNAPSHOT

_LOGGER: logging.Logger = logging.getLogger(__name__)

MAP_FOLDER_EXCLUDE = {
    FOLDER_HOMEASSISTANT: [
        "*.db-wal",
        "*.db-shm",
        "__pycache__/*",
        "*.log",
        "OZW_Log.txt",
    ]
}


class Snapshot(CoreSysAttributes):
    """A single Hass.io snapshot."""

    def __init__(self, coresys: CoreSys, tar_file: Path):
        """Initialize a snapshot."""
        self.coresys: CoreSys = coresys
        self._tarfile: Path = tar_file
        self._data: Dict[str, Any] = {}
        self._tmp = None
        self._key: Optional[bytes] = None
        self._aes: Optional[Cipher] = None

    @property
    def slug(self):
        """Return snapshot slug."""
        return self._data.get(ATTR_SLUG)

    @property
    def sys_type(self):
        """Return snapshot type."""
        return self._data.get(ATTR_TYPE)

    @property
    def name(self):
        """Return snapshot name."""
        return self._data[ATTR_NAME]

    @property
    def date(self):
        """Return snapshot date."""
        return self._data[ATTR_DATE]

    @property
    def protected(self):
        """Return snapshot date."""
        return self._data.get(ATTR_PROTECTED) is not None

    @property
    def addons(self):
        """Return snapshot date."""
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
        """Return snapshot date."""
        return self._data[ATTR_REPOSITORIES]

    @repositories.setter
    def repositories(self, value):
        """Set snapshot date."""
        self._data[ATTR_REPOSITORIES] = value

    @property
    def homeassistant_version(self):
        """Return snapshot Home Assistant version."""
        return self._data[ATTR_HOMEASSISTANT].get(ATTR_VERSION)

    @property
    def homeassistant(self):
        """Return snapshot Home Assistant data."""
        return self._data[ATTR_HOMEASSISTANT]

    @property
    def size(self):
        """Return snapshot size."""
        if not self.tarfile.is_file():
            return 0
        return round(self.tarfile.stat().st_size / 1048576, 2)  # calc mbyte

    @property
    def is_new(self):
        """Return True if there is new."""
        return not self.tarfile.exists()

    @property
    def tarfile(self):
        """Return path to Snapshot tarfile."""
        return self._tarfile

    def new(self, slug, name, date, sys_type, password=None):
        """Initialize a new snapshot."""
        # Init metadata
        self._data[ATTR_SLUG] = slug
        self._data[ATTR_NAME] = name
        self._data[ATTR_DATE] = date
        self._data[ATTR_TYPE] = sys_type

        # Add defaults
        self._data = SCHEMA_SNAPSHOT(self._data)

        # Set password
        if password:
            self._init_password(password)
            self._data[ATTR_PROTECTED] = password_for_validating(password)
            self._data[ATTR_CRYPTO] = CRYPTO_AES128

    def set_password(self, password: str) -> bool:
        """Set the password for an existing snapshot."""
        if not password:
            return False

        validating = password_for_validating(password)
        if validating != self._data[ATTR_PROTECTED]:
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
        """Read snapshot.json from tar file."""
        if not self.tarfile.is_file():
            _LOGGER.error("No tarfile %s", self.tarfile)
            return False

        def _load_file():
            """Read snapshot.json."""
            with tarfile.open(self.tarfile, "r:") as snapshot:
                json_file = snapshot.extractfile("./snapshot.json")
                return json_file.read()

        # read snapshot.json
        try:
            raw = await self.sys_run_in_executor(_load_file)
        except (tarfile.TarError, KeyError) as err:
            _LOGGER.error("Can't read snapshot tarfile %s: %s", self.tarfile, err)
            return False

        # parse data
        try:
            raw_dict = json.loads(raw)
        except json.JSONDecodeError as err:
            _LOGGER.error("Can't read data for %s: %s", self.tarfile, err)
            return False

        # validate
        try:
            self._data = SCHEMA_SNAPSHOT(raw_dict)
        except vol.Invalid as err:
            _LOGGER.error(
                "Can't validate data for %s: %s",
                self.tarfile,
                humanize_error(raw_dict, err),
            )
            return False

        return True

    async def __aenter__(self):
        """Async context to open a snapshot."""
        self._tmp = TemporaryDirectory(dir=str(self.sys_config.path_tmp))

        # create a snapshot
        if not self.tarfile.is_file():
            return self

        # extract an existing snapshot
        def _extract_snapshot():
            """Extract a snapshot."""
            with tarfile.open(self.tarfile, "r:") as tar:
                tar.extractall(path=self._tmp.name, members=secure_path(tar))

        await self.sys_run_in_executor(_extract_snapshot)

    async def __aexit__(self, exception_type, exception_value, traceback):
        """Async context to close a snapshot."""
        # exists snapshot or exception on build
        if self.tarfile.is_file() or exception_type is not None:
            self._tmp.cleanup()
            return

        # validate data
        try:
            self._data = SCHEMA_SNAPSHOT(self._data)
        except vol.Invalid as err:
            _LOGGER.error(
                "Invalid data for %s: %s", self.tarfile, humanize_error(self._data, err)
            )
            raise ValueError("Invalid config") from None

        # new snapshot, build it
        def _create_snapshot():
            """Create a new snapshot."""
            with tarfile.open(self.tarfile, "w:") as tar:
                tar.add(self._tmp.name, arcname=".")

        try:
            write_json_file(Path(self._tmp.name, "snapshot.json"), self._data)
            await self.sys_run_in_executor(_create_snapshot)
        except (OSError, json.JSONDecodeError) as err:
            _LOGGER.error("Can't write snapshot: %s", err)
        finally:
            self._tmp.cleanup()

    async def store_addons(self, addon_list=None):
        """Add a list of add-ons into snapshot."""
        addon_list = addon_list or self.sys_addons.installed

        async def _addon_save(addon):
            """Task to store an add-on into snapshot."""
            addon_file = SecureTarFile(
                Path(self._tmp.name, f"{addon.slug}.tar.gz"), "w", key=self._key
            )

            # Take snapshot
            try:
                await addon.snapshot(addon_file)
            except AddonsError:
                _LOGGER.error("Can't make snapshot from %s", addon.slug)
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

        # Run tasks
        tasks = [_addon_save(addon) for addon in addon_list]
        if tasks:
            await asyncio.wait(tasks)

    async def restore_addons(self, addon_list=None):
        """Restore a list add-on from snapshot."""
        addon_list = addon_list or self.addon_list

        async def _addon_restore(addon_slug):
            """Task to restore an add-on into snapshot."""
            addon_file = SecureTarFile(
                Path(self._tmp.name, f"{addon_slug}.tar.gz"), "r", key=self._key
            )

            # If exists inside snapshot
            if not addon_file.path.exists():
                _LOGGER.error("Can't find snapshot for %s", addon_slug)
                return

            # Perform a restore
            try:
                await self.sys_addons.restore(addon_slug, addon_file)
            except AddonsError:
                _LOGGER.error("Can't restore snapshot for %s", addon_slug)

        # Run tasks
        tasks = [_addon_restore(slug) for slug in addon_list]
        if tasks:
            await asyncio.wait(tasks)

    async def store_folders(self, folder_list=None):
        """Backup Hass.io data into snapshot."""
        folder_list = set(folder_list or ALL_FOLDERS)

        def _folder_save(name):
            """Internal function to snapshot a folder."""
            slug_name = name.replace("/", "_")
            tar_name = Path(self._tmp.name, f"{slug_name}.tar.gz")
            origin_dir = Path(self.sys_config.path_hassio, name)

            # Check if exists
            if not origin_dir.is_dir():
                _LOGGER.warning("Can't find snapshot folder %s", name)
                return

            # Take snapshot
            try:
                _LOGGER.info("Snapshot folder %s", name)
                with SecureTarFile(tar_name, "w", key=self._key) as tar_file:
                    tar_file.add(
                        origin_dir,
                        arcname=".",
                        filter=exclude_filter(MAP_FOLDER_EXCLUDE.get(name, [])),
                    )

                _LOGGER.info("Snapshot folder %s done", name)
                self._data[ATTR_FOLDERS].append(name)
            except (tarfile.TarError, OSError) as err:
                _LOGGER.warning("Can't snapshot folder %s: %s", name, err)

        # Run tasks
        tasks = [
            self.sys_run_in_executor(_folder_save, folder) for folder in folder_list
        ]
        if tasks:
            await asyncio.wait(tasks)

    async def restore_folders(self, folder_list=None):
        """Backup Hass.io data into snapshot."""
        folder_list = set(folder_list or self.folders)

        def _folder_restore(name):
            """Intenal function to restore a folder."""
            slug_name = name.replace("/", "_")
            tar_name = Path(self._tmp.name, f"{slug_name}.tar.gz")
            origin_dir = Path(self.sys_config.path_hassio, name)

            # Check if exists inside snapshot
            if not tar_name.exists():
                _LOGGER.warning("Can't find restore folder %s", name)
                return

            # Clean old stuff
            if origin_dir.is_dir():
                remove_folder(origin_dir)

            # Perform a restore
            try:
                _LOGGER.info("Restore folder %s", name)
                with SecureTarFile(tar_name, "r", key=self._key) as tar_file:
                    tar_file.extractall(path=origin_dir, members=tar_file)
                _LOGGER.info("Restore folder %s done", name)
            except (tarfile.TarError, OSError) as err:
                _LOGGER.warning("Can't restore folder %s: %s", name, err)

        # Run tasks
        tasks = [
            self.sys_run_in_executor(_folder_restore, folder) for folder in folder_list
        ]
        if tasks:
            await asyncio.wait(tasks)

    def store_homeassistant(self):
        """Read all data from Home Assistant object."""
        self.homeassistant[ATTR_VERSION] = self.sys_homeassistant.version
        self.homeassistant[ATTR_WATCHDOG] = self.sys_homeassistant.watchdog
        self.homeassistant[ATTR_BOOT] = self.sys_homeassistant.boot
        self.homeassistant[ATTR_WAIT_BOOT] = self.sys_homeassistant.wait_boot

        # Custom image
        if self.sys_homeassistant.is_custom_image:
            self.homeassistant[ATTR_IMAGE] = self.sys_homeassistant.image
            self.homeassistant[
                ATTR_LAST_VERSION
            ] = self.sys_homeassistant.latest_version

        # API/Proxy
        self.homeassistant[ATTR_PORT] = self.sys_homeassistant.api_port
        self.homeassistant[ATTR_SSL] = self.sys_homeassistant.api_ssl
        self.homeassistant[ATTR_REFRESH_TOKEN] = self._encrypt_data(
            self.sys_homeassistant.refresh_token
        )

    def restore_homeassistant(self):
        """Write all data to the Home Assistant object."""
        self.sys_homeassistant.watchdog = self.homeassistant[ATTR_WATCHDOG]
        self.sys_homeassistant.boot = self.homeassistant[ATTR_BOOT]
        self.sys_homeassistant.wait_boot = self.homeassistant[ATTR_WAIT_BOOT]

        # Custom image
        if self.homeassistant.get(ATTR_IMAGE):
            self.sys_homeassistant.image = self.homeassistant[ATTR_IMAGE]
            self.sys_homeassistant.latest_version = self.homeassistant[
                ATTR_LAST_VERSION
            ]

        # API/Proxy
        self.sys_homeassistant.api_port = self.homeassistant[ATTR_PORT]
        self.sys_homeassistant.api_ssl = self.homeassistant[ATTR_SSL]
        self.sys_homeassistant.refresh_token = self._decrypt_data(
            self.homeassistant[ATTR_REFRESH_TOKEN]
        )

        # save
        self.sys_homeassistant.save_data()

    def store_repositories(self):
        """Store repository list into snapshot."""
        self.repositories = self.sys_config.addons_repositories

    def restore_repositories(self):
        """Restore repositories from snapshot.

        Return a coroutine.
        """
        return self.sys_store.update_repositories(self.repositories)
