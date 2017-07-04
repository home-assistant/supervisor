"""Init file for HassIO snapshot rest api."""
import asyncio
import logging

import voluptuous as vol

from .util import api_process, api_validate
from ..snapshots.validate import ALL_FOLDERS
from ..const import (
    ATTR_NAME, ATTR_SLUG, ATTR_DATE, ATTR_ADDONS, ATTR_REPOSITORIES,
    ATTR_HOMEASSISTANT, ATTR_VERSION, ATTR_SIZE, ATTR_FOLDERS)

_LOGGER = logging.getLogger(__name__)


SCHEMA_PICK = vol.Schema({
    vol.Optional(ATTR_HOMEASSISTANT): vol.Boolean(),
    vol.Optional(ATTR_ADDONS): [vol.Coerce(str)],
    vol.Optional(ATTR_FOLDERS): [vol.In(ALL_FOLDERS)],
})

SCHEMA_SNAPSHOT = vol.Schema({
    vol.Optional(ATTR_NAME, default=""): vol.Coerce(str),
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

    def _addons_list(self, snapshot):
        """Generate a list with addons data."""
        data = []
        for addon_data in snapshot.addons:
            data.append({
                ATTR_SLUG: addon_data[ATTR_SLUG],
                ATTR_NAME: addon_data[ATTR_NAME],
                ATTR_VERSION: addon_data[ATTR_VERSION],
            })

        return data

    @api_process
    async def info(self, request):
        """Return snapshot info."""
        snapshot = self._extract_snapshot(request)

        return {
            ATTR_SLUG: snapshot.slug,
            ATTR_NAME: snapshot.name,
            ATTR_DATE: snapshot.date,
            ATTR_SIZE: snapshot.size,
            ATTR_HOMEASSISTANT: snapshot.homeassistant,
            ATTR_ADDONS: self._addons_list(snapshot),
            ATTR_REPOSITORIES: snapshot.repositories,
            ATTR_FOLDERS: snapshot.folders,
        }

    @api_process
    async def snapshot(self, request):
        """Full-Restore a snapshot."""
        body = await api_validate(SCHEMA_SNAPSHOT, request)
        return await asyncio.shield(
            self.snapshots.do_snapshot(body[ATTR_NAME]), loop=self.loop)

    @api_process
    async def restore(self, request):
        """Full-Restore a snapshot."""
        snapshot = self._extract_snapshot(request)
        return await asyncio.shield(
            self.snapshots.do_restore(snapshot), loop=self.loop)

    @api_process
    async def pick(self, request):
        """Full-Restore a snapshot."""
        snapshot = self._extract_snapshot(request)
        options = await api_validate(SCHEMA_PICK, request)

        return await asyncio.shield(
            self.snapshots.do_pick(snapshot, options), loop=self.loop)

    @api_process
    async def remove(self, request):
        """Full-Restore a snapshot."""
        snapshot = self._extract_snapshot(request)
        return self.snapshots.remove(snapshot)
