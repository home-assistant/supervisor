"""Init file for HassIO snapshot rest api."""
import asyncio
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from aiohttp import web
import voluptuous as vol

from .utils import api_process, api_validate
from ..snapshots.validate import ALL_FOLDERS
from ..const import (
    ATTR_NAME, ATTR_SLUG, ATTR_DATE, ATTR_ADDONS, ATTR_REPOSITORIES,
    ATTR_HOMEASSISTANT, ATTR_VERSION, ATTR_SIZE, ATTR_FOLDERS, ATTR_TYPE,
    ATTR_SNAPSHOTS, ATTR_PASSWORD, ATTR_PROTECTED, CONTENT_TYPE_TAR)
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


# pylint: disable=no-value-for-parameter
SCHEMA_RESTORE_PARTIAL = vol.Schema({
    vol.Optional(ATTR_PASSWORD): vol.Any(None, vol.Coerce(str)),
    vol.Optional(ATTR_HOMEASSISTANT): vol.Boolean(),
    vol.Optional(ATTR_ADDONS):
        vol.All([vol.Coerce(str)], vol.Unique()),
    vol.Optional(ATTR_FOLDERS):
        vol.All([vol.In(ALL_FOLDERS)], vol.Unique()),
})

SCHEMA_RESTORE_FULL = vol.Schema({
    vol.Optional(ATTR_PASSWORD): vol.Any(None, vol.Coerce(str)),
})

SCHEMA_SNAPSHOT_FULL = vol.Schema({
    vol.Optional(ATTR_NAME): vol.Coerce(str),
    vol.Optional(ATTR_PASSWORD): vol.Any(None, vol.Coerce(str)),
})

SCHEMA_SNAPSHOT_PARTIAL = SCHEMA_SNAPSHOT_FULL.extend({
    vol.Optional(ATTR_ADDONS):
        vol.All([vol.Coerce(str)], vol.Unique()),
    vol.Optional(ATTR_FOLDERS):
        vol.All([vol.In(ALL_FOLDERS)], vol.Unique()),
})


class APISnapshots(CoreSysAttributes):
    """Handle rest api for snapshot functions."""

    def _extract_snapshot(self, request):
        """Return addon and if not exists trow a exception."""
        snapshot = self._snapshots.get(request.match_info.get('snapshot'))
        if not snapshot:
            raise RuntimeError("Snapshot not exists")
        return snapshot

    @api_process
    async def list(self, request):
        """Return snapshot list."""
        data_snapshots = []
        for snapshot in self._snapshots.list_snapshots:
            data_snapshots.append({
                ATTR_SLUG: snapshot.slug,
                ATTR_NAME: snapshot.name,
                ATTR_DATE: snapshot.date,
                ATTR_TYPE: snapshot.sys_type,
                ATTR_PROTECTED: snapshot.protected,
            })

        return {
            ATTR_SNAPSHOTS: data_snapshots,
        }

    @api_process
    async def reload(self, request):
        """Reload snapshot list."""
        await asyncio.shield(self._snapshots.reload(), loop=self._loop)
        return True

    @api_process
    async def info(self, request):
        """Return snapshot info."""
        snapshot = self._extract_snapshot(request)

        data_addons = []
        for addon_data in snapshot.addons:
            data_addons.append({
                ATTR_SLUG: addon_data[ATTR_SLUG],
                ATTR_NAME: addon_data[ATTR_NAME],
                ATTR_VERSION: addon_data[ATTR_VERSION],
                ATTR_SIZE: addon_data[ATTR_SIZE],
            })

        return {
            ATTR_SLUG: snapshot.slug,
            ATTR_TYPE: snapshot.sys_type,
            ATTR_NAME: snapshot.name,
            ATTR_DATE: snapshot.date,
            ATTR_SIZE: snapshot.size,
            ATTR_PROTECTED: snapshot.protected,
            ATTR_HOMEASSISTANT: snapshot.homeassistant_version,
            ATTR_ADDONS: data_addons,
            ATTR_REPOSITORIES: snapshot.repositories,
            ATTR_FOLDERS: snapshot.folders,
        }

    @api_process
    async def snapshot_full(self, request):
        """Full-Snapshot a snapshot."""
        body = await api_validate(SCHEMA_SNAPSHOT_FULL, request)
        return await asyncio.shield(
            self._snapshots.do_snapshot_full(**body), loop=self._loop)

    @api_process
    async def snapshot_partial(self, request):
        """Partial-Snapshot a snapshot."""
        body = await api_validate(SCHEMA_SNAPSHOT_PARTIAL, request)
        return await asyncio.shield(
            self._snapshots.do_snapshot_partial(**body), loop=self._loop)

    @api_process
    async def restore_full(self, request):
        """Full-Restore a snapshot."""
        snapshot = self._extract_snapshot(request)
        body = await api_validate(SCHEMA_RESTORE_FULL, request)

        return await asyncio.shield(
            self._snapshots.do_restore_full(snapshot, **body),
            loop=self._loop
        )

    @api_process
    async def restore_partial(self, request):
        """Partial-Restore a snapshot."""
        snapshot = self._extract_snapshot(request)
        body = await api_validate(SCHEMA_RESTORE_PARTIAL, request)

        return await asyncio.shield(
            self._snapshots.do_restore_partial(snapshot, **body),
            loop=self._loop
        )

    @api_process
    async def remove(self, request):
        """Remove a snapshot."""
        snapshot = self._extract_snapshot(request)
        return self._snapshots.remove(snapshot)

    async def download(self, request):
        """Download a snapshot file."""
        snapshot = self._extract_snapshot(request)

        _LOGGER.info("Download snapshot %s", snapshot.slug)
        response = web.FileResponse(snapshot.tarfile)
        response.content_type = CONTENT_TYPE_TAR
        return response

    @api_process
    async def upload(self, request):
        """Upload a snapshot file."""
        with TemporaryDirectory(dir=str(self._config.path_tmp)) as temp_dir:
            tar_file = Path(temp_dir, f"snapshot.tar")

            try:
                with tar_file.open('wb') as snapshot:
                    async for data in request.content.iter_any():
                        snapshot.write(data)

            except OSError as err:
                _LOGGER.error("Can't write new snapshot file: %s", err)
                return False

            except asyncio.CancelledError:
                return False

            return await asyncio.shield(
                self._snapshots.import_snapshot(tar_file), loop=self._loop)
