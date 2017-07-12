"""Init file for HassIO snapshot rest api."""
import asyncio
import logging

import voluptuous as vol

from .util import api_process, api_validate
from ..snapshots.validate import ALL_FOLDERS
from ..const import (
    ATTR_NAME, ATTR_SLUG, ATTR_DATE, ATTR_ADDONS, ATTR_REPOSITORIES,
    ATTR_HOMEASSISTANT, ATTR_VERSION, ATTR_SIZE, ATTR_FOLDERS, ATTR_TYPE,
    ATTR_DEVICES, ATTR_SNAPSHOTS)

_LOGGER = logging.getLogger(__name__)


# pylint: disable=no-value-for-parameter
SCHEMA_RESTORE_PARTIAL = vol.Schema({
    vol.Optional(ATTR_HOMEASSISTANT): vol.Boolean(),
    vol.Optional(ATTR_ADDONS): [vol.Coerce(str)],
    vol.Optional(ATTR_FOLDERS): [vol.In(ALL_FOLDERS)],
})

SCHEMA_SNAPSHOT_FULL = vol.Schema({
    vol.Optional(ATTR_NAME): vol.Coerce(str),
})

SCHEMA_SNAPSHOT_PARTIAL = SCHEMA_SNAPSHOT_FULL.extend({
    vol.Optional(ATTR_ADDONS): [vol.Coerce(str)],
    vol.Optional(ATTR_FOLDERS): [vol.In(ALL_FOLDERS)],
})


class APISnapshots(object):
    """Handle rest api for snapshot functions."""

    def __init__(self, config, loop, snapshots):
        """Initialize network rest api part."""
        self.config = config
        self.loop = loop
        self.snapshots = snapshots

    def _extract_snapshot(self, request):
        """Return addon and if not exists trow a exception."""
        snapshot = self.snapshots.get(request.match_info.get('snapshot'))
        if not snapshot:
            raise RuntimeError("Snapshot not exists")
        return snapshot

    @api_process
    async def list(self, request):
        """Return snapshot list."""
        data_snapshots = []
        for snapshot in self.snapshots.list_snapshots:
            data_snapshots.append({
                ATTR_SLUG: snapshot.slug,
                ATTR_NAME: snapshot.name,
                ATTR_DATE: snapshot.date,
            })

        return {
            ATTR_SNAPSHOTS: data_snapshots,
        }

    @api_process
    def reload(self, request):
        """Reload snapshot list."""
        return asyncio.shield(self.snapshots.reload(), loop=self.loop)

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
            })

        return {
            ATTR_SLUG: snapshot.slug,
            ATTR_TYPE: snapshot.sys_type,
            ATTR_NAME: snapshot.name,
            ATTR_DATE: snapshot.date,
            ATTR_SIZE: snapshot.size,
            ATTR_HOMEASSISTANT: {
                ATTR_VERSION: snapshot.homeassistant_version,
                ATTR_DEVICES: snapshot.homeassistant_devices,
            },
            ATTR_ADDONS: data_addons,
            ATTR_REPOSITORIES: snapshot.repositories,
            ATTR_FOLDERS: snapshot.folders,
        }

    @api_process
    async def snapshot_full(self, request):
        """Full-Snapshot a snapshot."""
        body = await api_validate(SCHEMA_SNAPSHOT_FULL, request)
        return await asyncio.shield(
            self.snapshots.do_snapshot_full(**body), loop=self.loop)

    @api_process
    async def snapshot_partial(self, request):
        """Partial-Snapshot a snapshot."""
        body = await api_validate(SCHEMA_SNAPSHOT_PARTIAL, request)
        return await asyncio.shield(
            self.snapshots.do_snapshot_partial(**body), loop=self.loop)

    @api_process
    async def restore_full(self, request):
        """Full-Restore a snapshot."""
        snapshot = self._extract_snapshot(request)
        return await asyncio.shield(
            self.snapshots.do_restore_full(snapshot), loop=self.loop)

    @api_process
    async def restore_partial(self, request):
        """Partial-Restore a snapshot."""
        snapshot = self._extract_snapshot(request)
        body = await api_validate(SCHEMA_SNAPSHOT_PARTIAL, request)

        return await asyncio.shield(
            self.snapshots.do_restore_partial(snapshot, **body),
            loop=self.loop)

    @api_process
    async def remove(self, request):
        """Remove a snapshot."""
        snapshot = self._extract_snapshot(request)
        return self.snapshots.remove(snapshot)
