"""Validation for mount manager."""

import re
from typing import Any, NotRequired, TypedDict

import voluptuous as vol

from ..const import (
    ATTR_NAME,
    ATTR_PASSWORD,
    ATTR_PORT,
    ATTR_TYPE,
    ATTR_USERNAME,
    ATTR_VERSION,
)
from ..validate import network_port
from .const import (
    ATTR_DEFAULT_BACKUP_MOUNT,
    ATTR_MOUNTS,
    ATTR_PATH,
    ATTR_READ_ONLY,
    ATTR_SERVER,
    ATTR_SHARE,
    ATTR_USAGE,
    MountCifsVersion,
    MountType,
    MountUsage,
)


def usage_specific_validation(config: dict[str, Any]) -> dict[str, Any]:
    """Validate config based on usage."""
    # Backup mounts cannot be read only
    if config[ATTR_USAGE] == MountUsage.BACKUP and config[ATTR_READ_ONLY]:
        raise vol.Invalid("Backup mounts cannot be read only")

    return config


# pylint: disable=no-value-for-parameter

RE_MOUNT_NAME = re.compile(r"^[A-Za-z0-9_]+$")
RE_PATH_PART = re.compile(r"^[^\\\/]+")
RE_MOUNT_OPTION = re.compile(r"^[^,=]+$")

VALIDATE_NAME = vol.Match(RE_MOUNT_NAME)
VALIDATE_SERVER = vol.Match(RE_PATH_PART)
VALIDATE_SHARE = vol.Match(RE_PATH_PART)

_SCHEMA_BASE_MOUNT_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_NAME): VALIDATE_NAME,
        vol.Required(ATTR_TYPE): vol.All(
            vol.In([MountType.CIFS.value, MountType.NFS.value]), vol.Coerce(MountType)
        ),
        vol.Required(ATTR_USAGE): vol.Coerce(MountUsage),
        vol.Optional(ATTR_READ_ONLY, default=False): vol.Boolean(),
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
        vol.Required(ATTR_TYPE): vol.All(MountType.CIFS.value, vol.Coerce(MountType)),
        vol.Required(ATTR_SHARE): VALIDATE_SHARE,
        vol.Inclusive(ATTR_USERNAME, "basic_auth"): str,
        vol.Inclusive(ATTR_PASSWORD, "basic_auth"): str,
        vol.Optional(ATTR_VERSION, default=None): vol.Maybe(
            vol.Coerce(MountCifsVersion)
        ),
    }
)

SCHEMA_MOUNT_NFS = _SCHEMA_MOUNT_NETWORK.extend(
    {
        vol.Required(ATTR_TYPE): vol.All(MountType.NFS.value, vol.Coerce(MountType)),
        vol.Required(ATTR_PATH): str,
    }
)

SCHEMA_MOUNT_CONFIG = vol.All(
    vol.Any(SCHEMA_MOUNT_CIFS, SCHEMA_MOUNT_NFS), usage_specific_validation
)

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
    read_only: bool
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
