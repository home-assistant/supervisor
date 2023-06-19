"""Validation for mount manager."""

import re
from typing import TypedDict

from typing_extensions import NotRequired
import voluptuous as vol

from ..const import ATTR_NAME, ATTR_PASSWORD, ATTR_PORT, ATTR_TYPE, ATTR_USERNAME
from ..validate import network_port
from .const import (
    ATTR_CIFS_VERSION,
    ATTR_DEFAULT_BACKUP_MOUNT,
    ATTR_MOUNTS,
    ATTR_PATH,
    ATTR_SERVER,
    ATTR_SHARE,
    ATTR_USAGE,
    MountCifsVersion,
    MountType,
    MountUsage,
)

RE_MOUNT_NAME = re.compile(r"^\w+$")
RE_PATH_PART = re.compile(r"^[^\\\/]+")
RE_MOUNT_OPTION = re.compile(r"^[^,=]+$")

VALIDATE_NAME = vol.Match(RE_MOUNT_NAME)
VALIDATE_SERVER = vol.Match(RE_PATH_PART)
VALIDATE_SHARE = vol.Match(RE_PATH_PART)
VALIDATE_USERNAME = vol.Match(RE_MOUNT_OPTION)
VALIDATE_PASSWORD = vol.Match(RE_MOUNT_OPTION)

_SCHEMA_BASE_MOUNT_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_NAME): VALIDATE_NAME,
        vol.Required(ATTR_TYPE): vol.In([MountType.CIFS.value, MountType.NFS.value]),
        vol.Required(ATTR_USAGE): vol.In([u.value for u in MountUsage]),
    },
    extra=vol.REMOVE_EXTRA,
)

_SCHEMA_MOUNT_NETWORK = _SCHEMA_BASE_MOUNT_CONFIG.extend(
    {
        vol.Required(ATTR_SERVER): VALIDATE_SERVER,
        vol.Optional(ATTR_PORT): network_port,
    }
)

SCHEMA_MOUNT_CIFS = _SCHEMA_MOUNT_NETWORK.extend(
    {
        vol.Required(ATTR_TYPE): MountType.CIFS.value,
        vol.Required(ATTR_SHARE): VALIDATE_SHARE,
        vol.Inclusive(ATTR_USERNAME, "basic_auth"): VALIDATE_USERNAME,
        vol.Inclusive(ATTR_PASSWORD, "basic_auth"): VALIDATE_PASSWORD,
        vol.Optional(ATTR_CIFS_VERSION, default=None): vol.Maybe(
            vol.Coerce(MountCifsVersion)
        ),
    }
)

SCHEMA_MOUNT_NFS = _SCHEMA_MOUNT_NETWORK.extend(
    {
        vol.Required(ATTR_TYPE): MountType.NFS.value,
        vol.Required(ATTR_PATH): str,
    }
)

SCHEMA_MOUNT_CONFIG = vol.Any(SCHEMA_MOUNT_CIFS, SCHEMA_MOUNT_NFS)

SCHEMA_MOUNTS_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_MOUNTS, default=[]): [SCHEMA_MOUNT_CONFIG],
        vol.Optional(ATTR_DEFAULT_BACKUP_MOUNT): vol.Maybe(str),
    }
)


class MountData(TypedDict):
    """Dictionary representation of mount."""

    name: str
    type: str
    usage: NotRequired[str]

    # CIFS and NFS fields
    server: NotRequired[str]
    port: NotRequired[int]

    # CIFS fields
    share: NotRequired[str]
    username: NotRequired[str]
    password: NotRequired[str]

    # NFS and Bind fields
    path: NotRequired[str]
