"""Init file for Supervisor snapshot RESTful API."""

from ..const import (
    ATTR_ADDONS,
    ATTR_CONTENT,
    ATTR_DATE,
    ATTR_FOLDERS,
    ATTR_HOMEASSISTANT,
    ATTR_NAME,
    ATTR_PROTECTED,
    ATTR_SLUG,
    ATTR_SNAPSHOTS,
    ATTR_TYPE,
)
from .backups import APIBackups
from .utils import api_process


class APISnapshots(APIBackups):
    """
    Handle RESTful API for snapshot functions.

    **deprecated**

    June 2021: /snapshots was renamed to /backups
    """

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
                    ATTR_CONTENT: {
                        ATTR_HOMEASSISTANT: snapshot.homeassistant_version is not None,
                        ATTR_ADDONS: snapshot.addon_list,
                        ATTR_FOLDERS: snapshot.folders,
                    },
                }
            )

        return {ATTR_SNAPSHOTS: data_snapshots}
