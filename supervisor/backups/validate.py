"""Validate some things around restore."""
import voluptuous as vol

from ..backups.const import BackupType
from ..const import (
    ATTR_ADDONS,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_BOOT,
    ATTR_COMPRESSED,
    ATTR_CRYPTO,
    ATTR_DATE,
    ATTR_DOCKER,
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
)
from ..validate import (
    SCHEMA_DOCKER_CONFIG,
    docker_image,
    network_port,
    repositories,
    version_tag,
)

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
        raise vol.Invalid("Invalid addon list in backup!") from None
    return addons_list


# pylint: disable=no-value-for-parameter
SCHEMA_BACKUP = vol.Schema(
    {
        vol.Required(ATTR_SLUG): str,
        vol.Required(ATTR_TYPE): vol.Coerce(BackupType),
        vol.Required(ATTR_NAME): str,
        vol.Required(ATTR_DATE): str,
        vol.Optional(ATTR_COMPRESSED, default=True): vol.Boolean(),
        vol.Inclusive(ATTR_PROTECTED, "encrypted"): vol.All(
            str, vol.Length(min=1, max=1)
        ),
        vol.Inclusive(ATTR_CRYPTO, "encrypted"): CRYPTO_AES128,
        vol.Optional(ATTR_HOMEASSISTANT, default=dict): vol.Schema(
            {
                vol.Optional(ATTR_VERSION): version_tag,
                vol.Optional(ATTR_IMAGE): docker_image,
                vol.Optional(ATTR_BOOT, default=True): vol.Boolean(),
                vol.Optional(ATTR_SSL, default=False): vol.Boolean(),
                vol.Optional(ATTR_PORT, default=8123): network_port,
                vol.Optional(ATTR_REFRESH_TOKEN): vol.Maybe(str),
                vol.Optional(ATTR_WATCHDOG, default=True): vol.Boolean(),
                vol.Optional(ATTR_WAIT_BOOT, default=600): vol.All(
                    vol.Coerce(int), vol.Range(min=60)
                ),
                vol.Optional(ATTR_AUDIO_OUTPUT, default=None): vol.Maybe(str),
                vol.Optional(ATTR_AUDIO_INPUT, default=None): vol.Maybe(str),
            },
            extra=vol.REMOVE_EXTRA,
        ),
        vol.Optional(ATTR_DOCKER, default=dict): SCHEMA_DOCKER_CONFIG,
        vol.Optional(ATTR_FOLDERS, default=list): vol.All(
            [vol.In(ALL_FOLDERS)], vol.Unique()
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
