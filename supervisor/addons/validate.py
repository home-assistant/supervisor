"""Validate add-ons options schema."""
import logging
import re
import secrets
from typing import Any, Dict
import uuid

import voluptuous as vol

from ..const import (
    ARCH_ALL,
    ATTR_ACCESS_TOKEN,
    ATTR_ADVANCED,
    ATTR_APPARMOR,
    ATTR_ARCH,
    ATTR_ARGS,
    ATTR_AUDIO,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_AUTH_API,
    ATTR_AUTO_UPDATE,
    ATTR_BOOT,
    ATTR_BUILD_FROM,
    ATTR_CONFIGURATION,
    ATTR_DESCRIPTON,
    ATTR_DEVICES,
    ATTR_DEVICETREE,
    ATTR_DISCOVERY,
    ATTR_DOCKER_API,
    ATTR_ENVIRONMENT,
    ATTR_FULL_ACCESS,
    ATTR_GPIO,
    ATTR_HASSIO_API,
    ATTR_HASSIO_ROLE,
    ATTR_HOMEASSISTANT,
    ATTR_HOMEASSISTANT_API,
    ATTR_HOST_DBUS,
    ATTR_HOST_IPC,
    ATTR_HOST_NETWORK,
    ATTR_HOST_PID,
    ATTR_IMAGE,
    ATTR_INGRESS,
    ATTR_INGRESS_ENTRY,
    ATTR_INGRESS_PANEL,
    ATTR_INGRESS_PORT,
    ATTR_INGRESS_TOKEN,
    ATTR_INIT,
    ATTR_JOURNALD,
    ATTR_KERNEL_MODULES,
    ATTR_LABELS,
    ATTR_LEGACY,
    ATTR_LOCATON,
    ATTR_MACHINE,
    ATTR_MAP,
    ATTR_NAME,
    ATTR_NETWORK,
    ATTR_OPTIONS,
    ATTR_PANEL_ADMIN,
    ATTR_PANEL_ICON,
    ATTR_PANEL_TITLE,
    ATTR_PORTS,
    ATTR_PORTS_DESCRIPTION,
    ATTR_PRIVILEGED,
    ATTR_PROTECTED,
    ATTR_REALTIME,
    ATTR_REPOSITORY,
    ATTR_SCHEMA,
    ATTR_SERVICES,
    ATTR_SLUG,
    ATTR_SNAPSHOT_EXCLUDE,
    ATTR_SNAPSHOT_POST,
    ATTR_SNAPSHOT_PRE,
    ATTR_SQUASH,
    ATTR_STAGE,
    ATTR_STARTUP,
    ATTR_STATE,
    ATTR_STDIN,
    ATTR_SYSTEM,
    ATTR_TIMEOUT,
    ATTR_TMPFS,
    ATTR_TRANSLATIONS,
    ATTR_UART,
    ATTR_UDEV,
    ATTR_URL,
    ATTR_USB,
    ATTR_USER,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_VIDEO,
    ATTR_WATCHDOG,
    ATTR_WEBUI,
    ROLE_ALL,
    ROLE_DEFAULT,
    AddonBoot,
    AddonStage,
    AddonStartup,
    AddonState,
)
from ..discovery.validate import valid_discovery_service
from ..docker.const import Capabilities
from ..validate import (
    docker_image,
    docker_ports,
    docker_ports_description,
    network_port,
    token,
    uuid_match,
    version_tag,
)
from .options import RE_SCHEMA_ELEMENT

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_VOLUME = re.compile(r"^(config|ssl|addons|backup|share|media)(?::(rw|ro))?$")
RE_SERVICE = re.compile(r"^(?P<service>mqtt|mysql):(?P<rights>provide|want|need)$")


RE_DOCKER_IMAGE_BUILD = re.compile(
    r"^([a-zA-Z\-\.:\d{}]+/)*?([\-\w{}]+)/([\-\w{}]+)(:[\.\-\w{}]+)?$"
)

SCHEMA_ELEMENT = vol.Match(RE_SCHEMA_ELEMENT)

RE_MACHINE = re.compile(
    r"^!?(?:"
    r"|intel-nuc"
    r"|generic-x86-64"
    r"|odroid-c2"
    r"|odroid-c4"
    r"|odroid-n2"
    r"|odroid-xu"
    r"|qemuarm-64"
    r"|qemuarm"
    r"|qemux86-64"
    r"|qemux86"
    r"|raspberrypi"
    r"|raspberrypi2"
    r"|raspberrypi3-64"
    r"|raspberrypi3"
    r"|raspberrypi4-64"
    r"|raspberrypi4"
    r"|tinker"
    r")$"
)


def _warn_addon_config(config: Dict[str, Any]):
    """Warn about miss configs."""
    name = config.get(ATTR_NAME)
    if not name:
        raise vol.Invalid("Invalid Add-on config!")

    if config.get(ATTR_FULL_ACCESS, False) and (
        config.get(ATTR_DEVICES)
        or config.get(ATTR_UART)
        or config.get(ATTR_USB)
        or config.get(ATTR_GPIO)
    ):
        _LOGGER.warning(
            "Add-on have full device access, and selective device access in the configuration. Please report this to the maintainer of %s",
            name,
        )

    return config


def _migrate_addon_config(protocol=False):
    """Migrate addon config."""

    def _migrate(config: Dict[str, Any]):
        name = config.get(ATTR_NAME)
        if not name:
            raise vol.Invalid("Invalid Add-on config!")

        # Startup 2018-03-30
        if config.get(ATTR_STARTUP) in ("before", "after"):
            value = config[ATTR_STARTUP]
            if protocol:
                _LOGGER.warning(
                    "Add-on config 'startup' with '%s' is deprecated. Please report this to the maintainer of %s",
                    value,
                    name,
                )
            if value == "before":
                config[ATTR_STARTUP] = AddonStartup.SERVICES.value
            elif value == "after":
                config[ATTR_STARTUP] = AddonStartup.APPLICATION.value

        # UART 2021-01-20
        if "auto_uart" in config:
            if protocol:
                _LOGGER.warning(
                    "Add-on config 'auto_uart' is deprecated, use 'uart'. Please report this to the maintainer of %s",
                    name,
                )
            config[ATTR_UART] = config.pop("auto_uart")

        # Device 2021-01-20
        if ATTR_DEVICES in config and any(":" in line for line in config[ATTR_DEVICES]):
            if protocol:
                _LOGGER.warning(
                    "Add-on config 'devices' use a deprecated format, the new format uses a list of paths only. Please report this to the maintainer of %s",
                    name,
                )
            config[ATTR_DEVICES] = [line.split(":")[0] for line in config[ATTR_DEVICES]]

        # TMPFS 2021-02-01
        if ATTR_TMPFS in config and not isinstance(config[ATTR_TMPFS], bool):
            if protocol:
                _LOGGER.warning(
                    "Add-on config 'tmpfs' use a deprecated format, new it's only a boolean. Please report this to the maintainer of %s",
                    name,
                )
            config[ATTR_TMPFS] = True

        return config

    return _migrate


# pylint: disable=no-value-for-parameter
_SCHEMA_ADDON_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_NAME): str,
        vol.Required(ATTR_VERSION): version_tag,
        vol.Required(ATTR_SLUG): str,
        vol.Required(ATTR_DESCRIPTON): str,
        vol.Required(ATTR_ARCH): [vol.In(ARCH_ALL)],
        vol.Optional(ATTR_MACHINE): vol.All([vol.Match(RE_MACHINE)], vol.Unique()),
        vol.Optional(ATTR_URL): vol.Url(),
        vol.Optional(ATTR_STARTUP, default=AddonStartup.APPLICATION): vol.Coerce(
            AddonStartup
        ),
        vol.Optional(ATTR_BOOT, default=AddonBoot.AUTO): vol.Coerce(AddonBoot),
        vol.Optional(ATTR_INIT, default=True): vol.Boolean(),
        vol.Optional(ATTR_ADVANCED, default=False): vol.Boolean(),
        vol.Optional(ATTR_STAGE, default=AddonStage.STABLE): vol.Coerce(AddonStage),
        vol.Optional(ATTR_PORTS): docker_ports,
        vol.Optional(ATTR_PORTS_DESCRIPTION): docker_ports_description,
        vol.Optional(ATTR_WATCHDOG): vol.Match(
            r"^(?:https?|\[PROTO:\w+\]|tcp):\/\/\[HOST\]:(\[PORT:\d+\]|\d+).*$"
        ),
        vol.Optional(ATTR_WEBUI): vol.Match(
            r"^(?:https?|\[PROTO:\w+\]):\/\/\[HOST\]:\[PORT:\d+\].*$"
        ),
        vol.Optional(ATTR_INGRESS, default=False): vol.Boolean(),
        vol.Optional(ATTR_INGRESS_PORT, default=8099): vol.Any(
            network_port, vol.Equal(0)
        ),
        vol.Optional(ATTR_INGRESS_ENTRY): str,
        vol.Optional(ATTR_PANEL_ICON, default="mdi:puzzle"): str,
        vol.Optional(ATTR_PANEL_TITLE): str,
        vol.Optional(ATTR_PANEL_ADMIN, default=True): vol.Boolean(),
        vol.Optional(ATTR_HOMEASSISTANT): vol.Maybe(version_tag),
        vol.Optional(ATTR_HOST_NETWORK, default=False): vol.Boolean(),
        vol.Optional(ATTR_HOST_PID, default=False): vol.Boolean(),
        vol.Optional(ATTR_HOST_IPC, default=False): vol.Boolean(),
        vol.Optional(ATTR_HOST_DBUS, default=False): vol.Boolean(),
        vol.Optional(ATTR_DEVICES): [str],
        vol.Optional(ATTR_UDEV, default=False): vol.Boolean(),
        vol.Optional(ATTR_TMPFS, default=False): vol.Boolean(),
        vol.Optional(ATTR_MAP, default=list): [vol.Match(RE_VOLUME)],
        vol.Optional(ATTR_ENVIRONMENT): {vol.Match(r"\w*"): str},
        vol.Optional(ATTR_PRIVILEGED): [vol.Coerce(Capabilities)],
        vol.Optional(ATTR_APPARMOR, default=True): vol.Boolean(),
        vol.Optional(ATTR_FULL_ACCESS, default=False): vol.Boolean(),
        vol.Optional(ATTR_AUDIO, default=False): vol.Boolean(),
        vol.Optional(ATTR_VIDEO, default=False): vol.Boolean(),
        vol.Optional(ATTR_GPIO, default=False): vol.Boolean(),
        vol.Optional(ATTR_USB, default=False): vol.Boolean(),
        vol.Optional(ATTR_UART, default=False): vol.Boolean(),
        vol.Optional(ATTR_DEVICETREE, default=False): vol.Boolean(),
        vol.Optional(ATTR_KERNEL_MODULES, default=False): vol.Boolean(),
        vol.Optional(ATTR_REALTIME, default=False): vol.Boolean(),
        vol.Optional(ATTR_HASSIO_API, default=False): vol.Boolean(),
        vol.Optional(ATTR_HASSIO_ROLE, default=ROLE_DEFAULT): vol.In(ROLE_ALL),
        vol.Optional(ATTR_HOMEASSISTANT_API, default=False): vol.Boolean(),
        vol.Optional(ATTR_STDIN, default=False): vol.Boolean(),
        vol.Optional(ATTR_LEGACY, default=False): vol.Boolean(),
        vol.Optional(ATTR_DOCKER_API, default=False): vol.Boolean(),
        vol.Optional(ATTR_AUTH_API, default=False): vol.Boolean(),
        vol.Optional(ATTR_SERVICES): [vol.Match(RE_SERVICE)],
        vol.Optional(ATTR_DISCOVERY): [valid_discovery_service],
        vol.Optional(ATTR_SNAPSHOT_EXCLUDE): [str],
        vol.Optional(ATTR_SNAPSHOT_PRE): str,
        vol.Optional(ATTR_SNAPSHOT_POST): str,
        vol.Optional(ATTR_OPTIONS, default={}): dict,
        vol.Optional(ATTR_SCHEMA, default={}): vol.Any(
            vol.Schema(
                {
                    str: vol.Any(
                        SCHEMA_ELEMENT,
                        [
                            vol.Any(
                                SCHEMA_ELEMENT,
                                {str: vol.Any(SCHEMA_ELEMENT, [SCHEMA_ELEMENT])},
                            )
                        ],
                        vol.Schema({str: vol.Any(SCHEMA_ELEMENT, [SCHEMA_ELEMENT])}),
                    )
                }
            ),
            False,
        ),
        vol.Optional(ATTR_IMAGE): docker_image,
        vol.Optional(ATTR_TIMEOUT, default=10): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=300)
        ),
        vol.Optional(ATTR_JOURNALD, default=False): vol.Boolean(),
    },
    extra=vol.REMOVE_EXTRA,
)

SCHEMA_ADDON_CONFIG = vol.All(
    _migrate_addon_config(True), _warn_addon_config, _SCHEMA_ADDON_CONFIG
)


# pylint: disable=no-value-for-parameter
SCHEMA_BUILD_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_BUILD_FROM, default=dict): vol.Schema(
            {vol.In(ARCH_ALL): vol.Match(RE_DOCKER_IMAGE_BUILD)}
        ),
        vol.Optional(ATTR_SQUASH, default=False): vol.Boolean(),
        vol.Optional(ATTR_ARGS, default=dict): vol.Schema({str: str}),
        vol.Optional(ATTR_LABELS, default=dict): vol.Schema({str: str}),
    },
    extra=vol.REMOVE_EXTRA,
)

SCHEMA_TRANSLATION_CONFIGURATION = vol.Schema(
    {
        vol.Required(ATTR_NAME): str,
        vol.Optional(ATTR_DESCRIPTON): vol.Maybe(str),
    },
    extra=vol.REMOVE_EXTRA,
)


SCHEMA_ADDON_TRANSLATIONS = vol.Schema(
    {
        vol.Optional(ATTR_CONFIGURATION): {str: SCHEMA_TRANSLATION_CONFIGURATION},
        vol.Optional(ATTR_NETWORK): {str: str},
    },
    extra=vol.REMOVE_EXTRA,
)


# pylint: disable=no-value-for-parameter
SCHEMA_ADDON_USER = vol.Schema(
    {
        vol.Required(ATTR_VERSION): version_tag,
        vol.Optional(ATTR_IMAGE): docker_image,
        vol.Optional(ATTR_UUID, default=lambda: uuid.uuid4().hex): uuid_match,
        vol.Optional(ATTR_ACCESS_TOKEN): token,
        vol.Optional(ATTR_INGRESS_TOKEN, default=secrets.token_urlsafe): str,
        vol.Optional(ATTR_OPTIONS, default=dict): dict,
        vol.Optional(ATTR_AUTO_UPDATE, default=False): vol.Boolean(),
        vol.Optional(ATTR_BOOT): vol.Coerce(AddonBoot),
        vol.Optional(ATTR_NETWORK): docker_ports,
        vol.Optional(ATTR_AUDIO_OUTPUT): vol.Maybe(str),
        vol.Optional(ATTR_AUDIO_INPUT): vol.Maybe(str),
        vol.Optional(ATTR_PROTECTED, default=True): vol.Boolean(),
        vol.Optional(ATTR_INGRESS_PANEL, default=False): vol.Boolean(),
        vol.Optional(ATTR_WATCHDOG, default=False): vol.Boolean(),
    },
    extra=vol.REMOVE_EXTRA,
)

SCHEMA_ADDON_SYSTEM = vol.All(
    _migrate_addon_config(),
    _SCHEMA_ADDON_CONFIG.extend(
        {
            vol.Required(ATTR_LOCATON): str,
            vol.Required(ATTR_REPOSITORY): str,
            vol.Required(ATTR_TRANSLATIONS, default=dict): {
                str: SCHEMA_ADDON_TRANSLATIONS
            },
        }
    ),
)


SCHEMA_ADDONS_FILE = vol.Schema(
    {
        vol.Optional(ATTR_USER, default=dict): {str: SCHEMA_ADDON_USER},
        vol.Optional(ATTR_SYSTEM, default=dict): {str: SCHEMA_ADDON_SYSTEM},
    },
    extra=vol.REMOVE_EXTRA,
)


SCHEMA_ADDON_SNAPSHOT = vol.Schema(
    {
        vol.Required(ATTR_USER): SCHEMA_ADDON_USER,
        vol.Required(ATTR_SYSTEM): SCHEMA_ADDON_SYSTEM,
        vol.Required(ATTR_STATE): vol.Coerce(AddonState),
        vol.Required(ATTR_VERSION): version_tag,
    },
    extra=vol.REMOVE_EXTRA,
)
