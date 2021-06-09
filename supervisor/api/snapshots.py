"""Backups RESTful API."""
import asyncio
import logging
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from aiohttp import web
from aiohttp.hdrs import CONTENT_DISPOSITION
import voluptuous as vol

from ..const import (
    ATTR_ADDONS,
    ATTR_BACKUPS,
    ATTR_CONTENT,
    ATTR_DATE,
    ATTR_FOLDERS,
    ATTR_HOMEASSISTANT,
    ATTR_NAME,
    ATTR_PASSWORD,
    ATTR_PROTECTED,
    ATTR_REPOSITORIES,
    ATTR_SIZE,
    ATTR_SLUG,
    ATTR_SNAPSHOTS,
    ATTR_TYPE,
    ATTR_VERSION,
    CONTENT_TYPE_TAR,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..snapshots.validate import ALL_FOLDERS
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_SLUGIFY_NAME = re.compile(r"[^A-Za-z0-9]+")

# pylint: disable=no-value-for-parameter
SCHEMA_RESTORE_PARTIAL = vol.Schema(
    {
        vol.Optional(ATTR_PASSWORD): vol.Any(None, vol.Coerce(str)),
        vol.Optional(ATTR_HOMEASSISTANT): vol.Boolean(),
        vol.Optional(ATTR_ADDONS): vol.All([vol.Coerce(str)], vol.Unique()),
        vol.Optional(ATTR_FOLDERS): vol.All([vol.In(ALL_FOLDERS)], vol.Unique()),
    }
)

SCHEMA_RESTORE_FULL = vol.Schema(
    {vol.Optional(ATTR_PASSWORD): vol.Any(None, vol.Coerce(str))}
)

SCHEMA_SNAPSHOT_FULL = vol.Schema(
    {
        vol.Optional(ATTR_NAME): vol.Coerce(str),
        vol.Optional(ATTR_PASSWORD): vol.Any(None, vol.Coerce(str)),
    }
)

SCHEMA_SNAPSHOT_PARTIAL = SCHEMA_SNAPSHOT_FULL.extend(
    {
        vol.Optional(ATTR_ADDONS): vol.All([vol.Coerce(str)], vol.Unique()),
        vol.Optional(ATTR_FOLDERS): vol.All([vol.In(ALL_FOLDERS)], vol.Unique()),
        vol.Optional(ATTR_HOMEASSISTANT): vol.Boolean(),
    }
)


class APISnapshots(CoreSysAttributes):
    """Handle RESTful API for snapshots functions."""

    def _extract_slug(self, request):
        """Return backup, throw an exception if it doesn't exist."""
        backup = self.sys_snapshots.get(request.match_info.get("slug"))
        if not backup:
            raise APIError("Backup does not exist")
        return backup

    @api_process
    async def list(self, request):
        """Return backup list."""
        data_backups = []
        for backup in self.sys_snapshots.list_snapshots:
            data_backups.append(
                {
                    ATTR_SLUG: backup.slug,
                    ATTR_NAME: backup.name,
                    ATTR_DATE: backup.date,
                    ATTR_TYPE: backup.sys_type,
                    ATTR_PROTECTED: backup.protected,
                    ATTR_CONTENT: {
                        ATTR_HOMEASSISTANT: backup.homeassistant_version is not None,
                        ATTR_ADDONS: backup.addon_list,
                        ATTR_FOLDERS: backup.folders,
                    },
                }
            )

        return {ATTR_BACKUPS: data_backups}

    @api_process
    async def legacy_list(self, request):
        """Return snapshot list."""
        data_snapshots = []
        for snapshot in self.sys_snapshots.list_snapshots:
            data_snapshots.append(
                {
                    ATTR_SLUG: snapshot.slug,
                    ATTR_NAME: snapshot.name,
                    ATTR_DATE: snapshot.date,
                    ATTR_TYPE: snapshot.sys_type,
                    ATTR_PROTECTED: snapshot.protected,
                    ATTR_CONTENT: {
                        ATTR_HOMEASSISTANT: snapshot.homeassistant_version is not None,
                        ATTR_ADDONS: snapshot.addon_list,
                        ATTR_FOLDERS: snapshot.folders,
                    },
                }
            )

        return {ATTR_SNAPSHOTS: data_snapshots}

    @api_process
    async def reload(self, request):
        """Reload backup list."""
        await asyncio.shield(self.sys_snapshots.reload())
        return True

    @api_process
    async def info(self, request):
        """Return backup info."""
        backup = self._extract_slug(request)

        data_addons = []
        for addon_data in backup.addons:
            data_addons.append(
                {
                    ATTR_SLUG: addon_data[ATTR_SLUG],
                    ATTR_NAME: addon_data[ATTR_NAME],
                    ATTR_VERSION: addon_data[ATTR_VERSION],
                    ATTR_SIZE: addon_data[ATTR_SIZE],
                }
            )

        return {
            ATTR_SLUG: backup.slug,
            ATTR_TYPE: backup.sys_type,
            ATTR_NAME: backup.name,
            ATTR_DATE: backup.date,
            ATTR_SIZE: backup.size,
            ATTR_PROTECTED: backup.protected,
            ATTR_HOMEASSISTANT: backup.homeassistant_version,
            ATTR_ADDONS: data_addons,
            ATTR_REPOSITORIES: backup.repositories,
            ATTR_FOLDERS: backup.folders,
        }

    @api_process
    async def backup_full(self, request):
        """Create full backup."""
        body = await api_validate(SCHEMA_SNAPSHOT_FULL, request)
        backup = await asyncio.shield(self.sys_snapshots.do_snapshot_full(**body))

        if backup:
            return {ATTR_SLUG: backup.slug}
        return False

    @api_process
    async def backup_partial(self, request):
        """Create a partial backup."""
        body = await api_validate(SCHEMA_SNAPSHOT_PARTIAL, request)
        snapshot = await asyncio.shield(self.sys_snapshots.do_snapshot_partial(**body))

        if snapshot:
            return {ATTR_SLUG: snapshot.slug}
        return False

    @api_process
    async def restore_full(self, request):
        """Full restore of a backup."""
        backup = self._extract_slug(request)
        body = await api_validate(SCHEMA_RESTORE_FULL, request)

        return await asyncio.shield(self.sys_snapshots.do_restore_full(backup, **body))

    @api_process
    async def restore_partial(self, request):
        """Partial restore a backup."""
        backup = self._extract_slug(request)
        body = await api_validate(SCHEMA_RESTORE_PARTIAL, request)

        return await asyncio.shield(
            self.sys_snapshots.do_restore_partial(backup, **body)
        )

    @api_process
    async def remove(self, request):
        """Remove a backup."""
        backup = self._extract_slug(request)
        return self.sys_snapshots.remove(backup)

    async def download(self, request):
        """Download a backup file."""
        backup = self._extract_slug(request)

        _LOGGER.info("Downloading backup %s", backup.slug)
        response = web.FileResponse(backup.tarfile)
        response.content_type = CONTENT_TYPE_TAR
        response.headers[
            CONTENT_DISPOSITION
        ] = f"attachment; filename={RE_SLUGIFY_NAME.sub('_', backup.name)}.tar"
        return response

    @api_process
    async def upload(self, request):
        """Upload a backup file."""
        with TemporaryDirectory(dir=str(self.sys_config.path_tmp)) as temp_dir:
            tar_file = Path(temp_dir, "backup.tar")
            reader = await request.multipart()
            contents = await reader.next()
            try:
                with tar_file.open("wb") as backup:
                    while True:
                        chunk = await contents.read_chunk()
                        if not chunk:
                            break
                        backup.write(chunk)

            except OSError as err:
                _LOGGER.error("Can't write new backup file: %s", err)
                return False

            except asyncio.CancelledError:
                return False

            backup = await asyncio.shield(self.sys_snapshots.import_snapshot(tar_file))

        if backup:
            return {ATTR_SLUG: backup.slug}
        return False
