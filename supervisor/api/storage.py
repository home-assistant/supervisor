"""Init file for the storage API."""

from pathlib import Path

from aiohttp import web

from ..coresys import CoreSysAttributes
from .utils import api_process

ATTR_MAX_DEPTH = "max_depth"


def get_dir_structure_sizes(path: Path, max_depth: int = 1):
    """Return a recursive dict of subdirectories and their sizes, only if size > 0.

    Excludes external mounts and symlinks to avoid counting files on other filesystems
    or following symlinks that could lead to infinite loops or incorrect sizes.
    """

    size = 0
    if not path.exists():
        return {"size": size}

    children = {}
    root_device = path.stat().st_dev

    for child in path.iterdir():
        if not child.is_dir():
            size += child.stat(follow_symlinks=False).st_size
            continue

        # Skip symlinks to avoid infinite loops
        if child.is_symlink():
            continue

        try:
            # Skip if not on same device (external mount)
            if child.stat().st_dev != root_device:
                continue
        except (OSError, FileNotFoundError):
            continue

        child_result = get_dir_structure_sizes(child, max_depth - 1)
        if child_result["size"] > 0:
            size += child_result["size"]
            if max_depth > 1:
                children[child.name] = child_result

    if children:
        return {"size": size, "children": children}

    return {"size": size}


class APIStorage(CoreSysAttributes):
    """Handle RESTful API for storage usage."""

    @api_process
    async def usage(self, request: web.Request) -> dict:
        """Return a breakdown of storage usage for the system."""

        max_depth = request.query.get(ATTR_MAX_DEPTH, 1)
        try:
            max_depth = int(max_depth)
        except ValueError:
            max_depth = 1

        root_device = self.sys_config.path_homeassistant.stat().st_dev

        async def dir_info(path):
            return await self.sys_run_in_executor(
                get_dir_structure_sizes, path, max_depth
            )

        addons = await dir_info(self.sys_config.path_addons_data)
        media = await dir_info(self.sys_config.path_media)
        share = await dir_info(self.sys_config.path_share)
        backup = await dir_info(self.sys_config.path_backup)
        tmp = await dir_info(self.sys_config.path_tmp)
        config = await dir_info(self.sys_config.path_homeassistant)

        return {
            # Separate by device to allow for future expansion. This may be changed to partition in the future.
            root_device: {
                "addons": addons,
                "media": media,
                "share": share,
                "backup": backup,
                "tmp": tmp,
                "config": config,
            }
        }
