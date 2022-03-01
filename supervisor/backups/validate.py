"""Validate some things around restore."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from ..backups.const import BackupType
from ..const import (
    ATTR_ADDONS,
    ATTR_COMPRESSED,
    ATTR_CRYPTO,
    ATTR_DATE,
    ATTR_DOCKER,
    ATTR_FOLDERS,
    ATTR_HOMEASSISTANT,
    ATTR_NAME,
    ATTR_PROTECTED,
    ATTR_REPOSITORIES,
    ATTR_SIZE,
    ATTR_SLUG,
    ATTR_TYPE,
    ATTR_VERSION,
    CRYPTO_AES128,
    FOLDER_ADDONS,
    FOLDER_HOMEASSISTANT,
    FOLDER_MEDIA,
    FOLDER_SHARE,
    FOLDER_SSL,
)
from ..validate import SCHEMA_DOCKER_CONFIG, repositories, version_tag

ALL_FOLDERS = [
    FOLDER_SHARE,
    FOLDER_ADDONS,
    FOLDER_SSL,
    FOLDER_MEDIA,
]


def unique_addons(addons_list):
    """Validate that an add-on is unique."""
    single = {addon[ATTR_SLUG] for addon in addons_list}

    if len(single) != len(addons_list):
        raise vol.Invalid("Invalid addon list in backup!") from None
    return addons_list


def v1_homeassistant(
    homeassistant_data: dict[str, Any] | None
) -> dict[str, Any] | None:
    """Cleanup homeassistant artefacts from v1."""
    if not homeassistant_data:
        return None

    if homeassistant_data.get(ATTR_VERSION) is None:
        return None

    return homeassistant_data


def v1_folderlist(folder_data: list[str]) -> list[str]:
    """Cleanup folder artefacts from v1."""
    if FOLDER_HOMEASSISTANT in folder_data:
        folder_data.remove(FOLDER_HOMEASSISTANT)
    return folder_data


# pylint: disable=no-value-for-parameter
SCHEMA_BACKUP = vol.Schema(
    {
        vol.Optional(ATTR_VERSION, default=1): vol.All(vol.Coerce(int), vol.In((1, 2))),
        vol.Required(ATTR_SLUG): str,
        vol.Required(ATTR_TYPE): vol.Coerce(BackupType),
        vol.Required(ATTR_NAME): str,
        vol.Required(ATTR_DATE): str,
        vol.Optional(ATTR_COMPRESSED, default=True): vol.Boolean(),
        vol.Optional(ATTR_PROTECTED, default=False): vol.Boolean(),
        vol.Optional(ATTR_CRYPTO, default=None): vol.Maybe(CRYPTO_AES128),
        vol.Optional(ATTR_HOMEASSISTANT, default=None): vol.All(
            v1_homeassistant,
            vol.Maybe(
                vol.Schema(
                    {
                        vol.Required(ATTR_VERSION): version_tag,
                        vol.Optional(ATTR_SIZE, default=0): vol.Coerce(float),
                    },
                    extra=vol.REMOVE_EXTRA,
                )
            ),
        ),
        vol.Optional(ATTR_DOCKER, default=dict): SCHEMA_DOCKER_CONFIG,
        vol.Optional(ATTR_FOLDERS, default=list): vol.All(
            v1_folderlist, [vol.In(ALL_FOLDERS)], vol.Unique()
        ),
        vol.Optional(ATTR_ADDONS, default=list): vol.All(
            [
                vol.Schema(
                    {
                        vol.Required(ATTR_SLUG): str,
                        vol.Required(ATTR_NAME): str,
                        vol.Required(ATTR_VERSION): version_tag,
                        vol.Optional(ATTR_SIZE, default=0): vol.Coerce(float),
                    },
                    extra=vol.REMOVE_EXTRA,
                )
            ],
            unique_addons,
        ),
        vol.Optional(ATTR_REPOSITORIES, default=list): repositories,
    },
    extra=vol.ALLOW_EXTRA,
)
