"""Validate some things around restore."""
import voluptuous as vol

from ..const import (
    ATTR_ADDONS,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_BOOT,
    ATTR_CRYPTO,
    ATTR_DATE,
    ATTR_FOLDERS,
    ATTR_HOMEASSISTANT,
    ATTR_IMAGE,
    ATTR_NAME,
    ATTR_PORT,
    ATTR_PROTECTED,
    ATTR_REFRESH_TOKEN,
    ATTR_REPOSITORIES,
    ATTR_SIZE,
    ATTR_SLUG,
    ATTR_SSL,
    ATTR_TYPE,
    ATTR_VERSION,
    ATTR_WAIT_BOOT,
    ATTR_WATCHDOG,
    CRYPTO_AES128,
    FOLDER_ADDONS,
    FOLDER_HOMEASSISTANT,
    FOLDER_MEDIA,
    FOLDER_SHARE,
    FOLDER_SSL,
    SNAPSHOT_FULL,
    SNAPSHOT_PARTIAL,
)
from ..validate import docker_image, network_port, repositories, version_tag

ALL_FOLDERS = [
    FOLDER_HOMEASSISTANT,
    FOLDER_SHARE,
    FOLDER_ADDONS,
    FOLDER_SSL,
    FOLDER_MEDIA,
]


def unique_addons(addons_list):
    """Validate that an add-on is unique."""
    single = {addon[ATTR_SLUG] for addon in addons_list}

    if len(single) != len(addons_list):
        raise vol.Invalid("Invalid addon list on snapshot!") from None
    return addons_list


# pylint: disable=no-value-for-parameter
SCHEMA_SNAPSHOT = vol.Schema(
    {
        vol.Required(ATTR_SLUG): vol.Coerce(str),
        vol.Required(ATTR_TYPE): vol.In([SNAPSHOT_FULL, SNAPSHOT_PARTIAL]),
        vol.Required(ATTR_NAME): vol.Coerce(str),
        vol.Required(ATTR_DATE): vol.Coerce(str),
        vol.Inclusive(ATTR_PROTECTED, "encrypted"): vol.All(
            vol.Coerce(str), vol.Length(min=1, max=1)
        ),
        vol.Inclusive(ATTR_CRYPTO, "encrypted"): CRYPTO_AES128,
        vol.Optional(ATTR_HOMEASSISTANT, default=dict): vol.Schema(
            {
                vol.Optional(ATTR_VERSION): version_tag,
                vol.Optional(ATTR_IMAGE): docker_image,
                vol.Optional(ATTR_BOOT, default=True): vol.Boolean(),
                vol.Optional(ATTR_SSL, default=False): vol.Boolean(),
                vol.Optional(ATTR_PORT, default=8123): network_port,
                vol.Optional(ATTR_REFRESH_TOKEN): vol.Maybe(vol.Coerce(str)),
                vol.Optional(ATTR_WATCHDOG, default=True): vol.Boolean(),
                vol.Optional(ATTR_WAIT_BOOT, default=600): vol.All(
                    vol.Coerce(int), vol.Range(min=60)
                ),
                vol.Optional(ATTR_AUDIO_OUTPUT, default=None): vol.Maybe(
                    vol.Coerce(str)
                ),
                vol.Optional(ATTR_AUDIO_INPUT, default=None): vol.Maybe(
                    vol.Coerce(str)
                ),
            },
            extra=vol.REMOVE_EXTRA,
        ),
        vol.Optional(ATTR_FOLDERS, default=list): vol.All(
            [vol.In(ALL_FOLDERS)], vol.Unique()
        ),
        vol.Optional(ATTR_ADDONS, default=list): vol.All(
            [
                vol.Schema(
                    {
                        vol.Required(ATTR_SLUG): vol.Coerce(str),
                        vol.Required(ATTR_NAME): vol.Coerce(str),
                        vol.Required(ATTR_VERSION): vol.Coerce(str),
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
