"""Init file for Supervisor snapshot RESTful API."""
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
    }
)


class APISnapshots(CoreSysAttributes):
    """Handle RESTful API for snapshot functions."""

    def _extract_snapshot(self, request):
        """Return snapshot, throw an exception if it doesn't exist."""
        snapshot = self.sys_snapshots.get(request.match_info.get("snapshot"))
        if not snapshot:
            raise APIError("Snapshot does not exist")
        return snapshot

    @api_process
    async def list(self, request):
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
                }
            )

        return {ATTR_SNAPSHOTS: data_snapshots}

    @api_process
    async def reload(self, request):
        """Reload snapshot list."""
        await asyncio.shield(self.sys_snapshots.reload())
        return True

    @api_process
    async def info(self, request):
        """Return snapshot info."""
        snapshot = self._extract_snapshot(request)

        data_addons = []
        for addon_data in snapshot.addons:
            data_addons.append(
                {
                    ATTR_SLUG: addon_data[ATTR_SLUG],
                    ATTR_NAME: addon_data[ATTR_NAME],
                    ATTR_VERSION: addon_data[ATTR_VERSION],
                    ATTR_SIZE: addon_data[ATTR_SIZE],
                }
            )

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
        snapshot = await asyncio.shield(self.sys_snapshots.do_snapshot_full(**body))

        if snapshot:
            return {ATTR_SLUG: snapshot.slug}
        return False

    @api_process
    async def snapshot_partial(self, request):
        """Partial-Snapshot a snapshot."""
        body = await api_validate(SCHEMA_SNAPSHOT_PARTIAL, request)
        snapshot = await asyncio.shield(self.sys_snapshots.do_snapshot_partial(**body))

        if snapshot:
            return {ATTR_SLUG: snapshot.slug}
        return False

    @api_process
    async def restore_full(self, request):
        """Full-Restore a snapshot."""
        snapshot = self._extract_snapshot(request)
        body = await api_validate(SCHEMA_RESTORE_FULL, request)

        return await asyncio.shield(
            self.sys_snapshots.do_restore_full(snapshot, **body)
        )

    @api_process
    async def restore_partial(self, request):
        """Partial-Restore a snapshot."""
        snapshot = self._extract_snapshot(request)
        body = await api_validate(SCHEMA_RESTORE_PARTIAL, request)

        return await asyncio.shield(
            self.sys_snapshots.do_restore_partial(snapshot, **body)
        )

    @api_process
    async def remove(self, request):
        """Remove a snapshot."""
        snapshot = self._extract_snapshot(request)
        return self.sys_snapshots.remove(snapshot)

    async def download(self, request):
        """Download a snapshot file."""
        snapshot = self._extract_snapshot(request)

        _LOGGER.info("Download snapshot %s", snapshot.slug)
        response = web.FileResponse(snapshot.tarfile)
        response.content_type = CONTENT_TYPE_TAR
        response.headers[
            CONTENT_DISPOSITION
        ] = f"attachment; filename={re.sub('[^A-Za-z0-9]+', '_', snapshot.name)}.tar"
        return response

    @api_process
    async def upload(self, request):
        """Upload a snapshot file."""
        with TemporaryDirectory(dir=str(self.sys_config.path_tmp)) as temp_dir:
            tar_file = Path(temp_dir, "snapshot.tar")
            reader = await request.multipart()
            contents = await reader.next()
            try:
                with tar_file.open("wb") as snapshot:
                    while True:
                        chunk = await contents.read_chunk()
                        if not chunk:
                            break
                        snapshot.write(chunk)

            except OSError as err:
                _LOGGER.error("Can't write new snapshot file: %s", err)
                return False

            except asyncio.CancelledError:
                return False

            snapshot = await asyncio.shield(
                self.sys_snapshots.import_snapshot(tar_file)
            )

        if snapshot:
            return {ATTR_SLUG: snapshot.slug}
        return False
