"""Validate apps options schema."""

from collections.abc import Callable
import logging
import re
import secrets
from typing import Any
import uuid

import voluptuous as vol

from ..const import (
    ARCH_ALL_COMPAT,
    ARCH_DEPRECATED,
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
    ATTR_BACKUP_EXCLUDE,
    ATTR_BACKUP_POST,
    ATTR_BACKUP_PRE,
    ATTR_BOOT,
    ATTR_BUILD_FROM,
    ATTR_CONFIGURATION,
    ATTR_DESCRIPTON,
    ATTR_DEVICES,
    ATTR_DEVICETREE,
    ATTR_DISCOVERY,
    ATTR_DOCKER_API,
    ATTR_ENVIRONMENT,
    ATTR_FIELDS,
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
    ATTR_HOST_UTS,
    ATTR_IMAGE,
    ATTR_INGRESS,
    ATTR_INGRESS_ENTRY,
    ATTR_INGRESS_PANEL,
    ATTR_INGRESS_PORT,
    ATTR_INGRESS_STREAM,
    ATTR_INGRESS_TOKEN,
    ATTR_INIT,
    ATTR_JOURNALD,
    ATTR_KERNEL_MODULES,
    ATTR_LABELS,
    ATTR_LEGACY,
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
    ATTR_SQUASH,
    ATTR_STAGE,
    ATTR_STARTUP,
    ATTR_STATE,
    ATTR_STDIN,
    ATTR_SYSTEM,
    ATTR_SYSTEM_MANAGED,
    ATTR_SYSTEM_MANAGED_CONFIG_ENTRY,
    ATTR_TIMEOUT,
    ATTR_TMPFS,
    ATTR_TRANSLATIONS,
    ATTR_TYPE,
    ATTR_UART,
    ATTR_UDEV,
    ATTR_ULIMITS,
    ATTR_URL,
    ATTR_USB,
    ATTR_USER,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_VIDEO,
    ATTR_WATCHDOG,
    ATTR_WATCHDOG_RESTART_POLICY,
    ATTR_WEBUI,
    INGRESS_DYNAMIC_PORT_MAX,
    INGRESS_DYNAMIC_PORT_MIN,
    MACHINE_DEPRECATED,
    ROLE_ALL,
    ROLE_DEFAULT,
    AppBoot,
    AppBootConfig,
    AppStage,
    AppStartup,
    AppState,
    WatchdogRestartPolicy,
)
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
from .const import (
    ATTR_BACKUP,
    ATTR_BREAKING_VERSIONS,
    ATTR_CODENOTARY,
    ATTR_PATH,
    ATTR_READ_ONLY,
    RE_SLUG,
    AppBackupMode,
    MappingType,
)
from .options import RE_SCHEMA_ELEMENT

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_VOLUME = re.compile(
    r"^(data|config|ssl|local_apps|addons|backup|share|media|homeassistant_config|all_app_configs|all_addon_configs|app_config|addon_config)(?::(rw|ro))?$"
)
RE_SERVICE = re.compile(r"^(?P<service>mqtt|mysql):(?P<rights>provide|want|need)$")


RE_DOCKER_IMAGE_BUILD = re.compile(
    r"^([a-zA-Z\-\.:\d{}]+/)*?([\-\w{}]+)/([\-\w{}]+)(:[\.\-\w{}]+)?$"
)

SCHEMA_ELEMENT = vol.Schema(
    vol.Any(
        vol.Match(RE_SCHEMA_ELEMENT),
        [
            # A list may not directly contain another list
            vol.Any(
                vol.Match(RE_SCHEMA_ELEMENT),
                {str: vol.Self},
            )
        ],
        {str: vol.Self},
    )
)

RE_MACHINE = re.compile(
    r"^!?(?:"
    r"|intel-nuc"
    r"|khadas-vim3"
    r"|generic-aarch64"
    r"|generic-x86-64"
    r"|odroid-c2"
    r"|odroid-c4"
    r"|odroid-m1"
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
    r"|raspberrypi5-64"
    r"|yellow"
    r"|green"
    r"|tinker"
    r")$"
)

RE_SLUG_FIELD = re.compile(r"^" + RE_SLUG + r"$")


def _warn_app_config(log: Callable[..., None]):
    """Build a validator that flags questionable app configs.

    Deprecation and misconfiguration advisories are emitted through ``log`` so
    the caller can pick the level appropriate for the audience (see
    SCHEMA_APP_CONFIG vs. SCHEMA_APP_CONFIG_QUIET). The messages are addressed at
    whoever can act on them (a local app's author or a developer on the dev
    channel), so they intentionally do not ask the reader to contact a
    maintainer.
    """

    def _warn(config: dict[str, Any]):
        name = config.get(ATTR_NAME)
        if not name:
            raise vol.Invalid("Invalid app config!")

        if ATTR_ADVANCED in config:
            # Deprecated since Supervisor 2026.03.0; this field is ignored and
            # the advisory can be removed once that version is the minimum
            # supported.
            log(
                "App '%s' uses the deprecated 'advanced' config field, which is ignored.",
                name,
            )

        if config.get(ATTR_FULL_ACCESS, False) and (
            config.get(ATTR_DEVICES)
            or config.get(ATTR_UART)
            or config.get(ATTR_USB)
            or config.get(ATTR_GPIO)
        ):
            log(
                "App '%s' has full device access; its selective device access configuration is redundant and ignored.",
                name,
            )

        if config.get(ATTR_BACKUP, AppBackupMode.HOT) == AppBackupMode.COLD and (
            config.get(ATTR_BACKUP_POST) or config.get(ATTR_BACKUP_PRE)
        ):
            log(
                "App '%s' only supports COLD backups but configures pre/post backup commands, which are ignored.",
                name,
            )

        if deprecated_arches := [
            arch for arch in config.get(ATTR_ARCH, []) if arch in ARCH_DEPRECATED
        ]:
            log(
                "App '%s' uses deprecated 'arch' values: %s",
                name,
                deprecated_arches,
            )

        if deprecated_machines := [
            machine
            for machine in config.get(ATTR_MACHINE, [])
            if machine.lstrip("!") in MACHINE_DEPRECATED
        ]:
            log(
                "App '%s' uses deprecated 'machine' values: %s",
                name,
                deprecated_machines,
            )

        if ATTR_CODENOTARY in config:
            log(
                "App '%s' uses the deprecated 'codenotary' config field, which is no longer used and ignored.",
                name,
            )

        # Deprecated map types, deprecated as of 2026.07
        _LEGACY_MAP_TYPES = {
            MappingType.ADDONS: MappingType.LOCAL_APPS,
            MappingType.ALL_ADDON_CONFIGS: MappingType.ALL_APP_CONFIGS,
            MappingType.ADDON_CONFIG: MappingType.APP_CONFIG,
        }
        for volume in config[ATTR_MAP]:
            if (volume_type := volume[ATTR_TYPE]) in _LEGACY_MAP_TYPES:
                log(
                    "App '%s' uses legacy map type '%s'; use '%s' instead.",
                    name,
                    volume_type,
                    _LEGACY_MAP_TYPES[volume_type],
                )

        # Dynamic ingress port selection (ingress_port: 0) picks a random port
        # from the INGRESS_DYNAMIC_PORT_MIN-INGRESS_DYNAMIC_PORT_MAX range. An
        # app must not map a port from that range to the host itself, as the
        # dynamically chosen ingress port could then coincide with it, exposing
        # the ingress endpoint on the host and bypassing ingress authentication.
        if config.get(ATTR_INGRESS) and config.get(ATTR_INGRESS_PORT) == 0:
            for container_port in config.get(ATTR_PORTS, {}):
                port_number = str(container_port).partition("/")[0]
                if (
                    port_number.isdigit()
                    and INGRESS_DYNAMIC_PORT_MIN
                    <= int(port_number)
                    <= INGRESS_DYNAMIC_PORT_MAX
                ):
                    raise vol.Invalid(
                        f"App '{name}' uses dynamic ingress port selection (ingress_port: 0) "
                        f"but maps port {port_number} which is reserved for dynamic ingress "
                        f"ports ({INGRESS_DYNAMIC_PORT_MIN}-{INGRESS_DYNAMIC_PORT_MAX}). "
                        "Please report this to the maintainer of the app."
                    )

        return config

    return _warn


def _migrate_app_config(log: Callable[..., None]):
    """Migrate app config.

    Deprecated-format advisories are emitted through ``log`` so the caller can
    pick the level appropriate for the audience (see SCHEMA_APP_CONFIG vs.
    SCHEMA_APP_CONFIG_QUIET). The migration itself always happens regardless of
    the level.
    """

    def _migrate(config: dict[str, Any]):
        if not isinstance(config, dict):
            raise vol.Invalid("App config must be a dictionary!")
        name = config.get(ATTR_NAME)
        if not name:
            raise vol.Invalid("Invalid app config!")

        # Startup 2018-03-30
        if config.get(ATTR_STARTUP) in ("before", "after"):
            value = config[ATTR_STARTUP]
            log(
                "App '%s' uses deprecated 'startup' value '%s'.",
                name,
                value,
            )
            if value == "before":
                config[ATTR_STARTUP] = AppStartup.SERVICES
            elif value == "after":
                config[ATTR_STARTUP] = AppStartup.APPLICATION

        # UART 2021-01-20
        if "auto_uart" in config:
            log(
                "App '%s' uses deprecated 'auto_uart'; use 'uart' instead.",
                name,
            )
            config[ATTR_UART] = config.pop("auto_uart")

        # Device 2021-01-20
        if ATTR_DEVICES in config and any(":" in line for line in config[ATTR_DEVICES]):
            log(
                "App '%s' uses a deprecated 'devices' format; use a list of paths only.",
                name,
            )
            config[ATTR_DEVICES] = [line.split(":")[0] for line in config[ATTR_DEVICES]]

        # TMPFS 2021-02-01
        if ATTR_TMPFS in config and not isinstance(config[ATTR_TMPFS], bool):
            log(
                "App '%s' uses a deprecated 'tmpfs' format; use a boolean instead.",
                name,
            )
            config[ATTR_TMPFS] = True

        # 2021-06 "snapshot" renamed to "backup"
        for entry in (
            "snapshot_exclude",
            "snapshot_post",
            "snapshot_pre",
            "snapshot",
        ):
            if entry in config:
                new_entry = entry.replace("snapshot", "backup")
                config[new_entry] = config.pop(entry)
                log(
                    "App '%s' uses deprecated config '%s'; use '%s' instead.",
                    name,
                    entry,
                    new_entry,
                )

        # 2023-11 "map" entries can also be dict to allow path configuration
        volumes = []
        for entry in config.get(ATTR_MAP, []):
            if isinstance(entry, dict):
                # Validate that dict entries have required 'type' field
                if ATTR_TYPE not in entry:
                    log(
                        "App '%s' has an invalid map entry missing the 'type' field, skipping: %s",
                        name,
                        entry,
                    )
                    continue
                volumes.append(entry)
            if isinstance(entry, str):
                result = RE_VOLUME.match(entry)
                if not result:
                    log(
                        "App '%s' has an invalid map entry, skipping: %s",
                        name,
                        entry,
                    )
                    continue
                volumes.append(
                    {
                        ATTR_TYPE: result.group(1),
                        ATTR_READ_ONLY: result.group(2) != "rw",
                    }
                )

        # Always update config to clear potentially malformed ones
        config[ATTR_MAP] = volumes

        # 2023-10 "config" became "homeassistant" so /config can be used for app's public config
        if any(volume[ATTR_TYPE] == MappingType.CONFIG for volume in volumes):
            if any(
                volume
                and volume[ATTR_TYPE]
                in {
                    MappingType.APP_CONFIG,
                    MappingType.ADDON_CONFIG,
                    MappingType.HOMEASSISTANT_CONFIG,
                }
                for volume in volumes
            ):
                log(
                    "App '%s' uses incompatible map options; '%s', '%s', and '%s' are ignored when '%s' is included.",
                    name,
                    MappingType.APP_CONFIG,
                    MappingType.ADDON_CONFIG,
                    MappingType.HOMEASSISTANT_CONFIG,
                    MappingType.CONFIG,
                )
            else:
                log(
                    "App '%s' uses deprecated map option '%s'; use '%s' instead.",
                    name,
                    MappingType.CONFIG,
                    MappingType.HOMEASSISTANT_CONFIG,
                )

        # 2026-07 addon-based map options replaced by app-based options.
        volume_types = {volume[ATTR_TYPE] for volume in volumes}
        for app_mapping_type, legacy_mapping_type in (
            (MappingType.LOCAL_APPS, MappingType.ADDONS),
            (MappingType.ALL_APP_CONFIGS, MappingType.ALL_ADDON_CONFIGS),
            (MappingType.APP_CONFIG, MappingType.ADDON_CONFIG),
        ):
            if {app_mapping_type, legacy_mapping_type} <= volume_types:
                log(
                    "App '%s' uses incompatible map options '%s' and '%s'; legacy option '%s' will be ignored.",
                    name,
                    app_mapping_type,
                    legacy_mapping_type,
                    legacy_mapping_type,
                )

        return config

    return _migrate


# pylint: disable=no-value-for-parameter
_SCHEMA_APP_CONFIG = vol.Schema(
    {
        vol.Required(ATTR_NAME): str,
        vol.Required(ATTR_VERSION): version_tag,
        vol.Required(ATTR_SLUG): vol.Match(RE_SLUG_FIELD),
        vol.Required(ATTR_DESCRIPTON): str,
        vol.Required(ATTR_ARCH): [vol.In(ARCH_ALL_COMPAT)],
        vol.Optional(ATTR_MACHINE): vol.All([vol.Match(RE_MACHINE)], vol.Unique()),
        vol.Optional(ATTR_URL): vol.Url(),
        vol.Optional(ATTR_STARTUP, default=AppStartup.APPLICATION): vol.Coerce(
            AppStartup
        ),
        vol.Optional(ATTR_BOOT, default=AppBootConfig.AUTO): vol.Coerce(AppBootConfig),
        vol.Optional(ATTR_INIT, default=True): vol.Boolean(),
        vol.Optional(ATTR_ADVANCED, default=False): vol.Boolean(),
        vol.Optional(ATTR_STAGE, default=AppStage.STABLE): vol.Coerce(AppStage),
        vol.Optional(ATTR_PORTS): docker_ports,
        vol.Optional(ATTR_PORTS_DESCRIPTION): docker_ports_description,
        vol.Optional(ATTR_WATCHDOG): vol.Match(
            r"^(?:https?|\[PROTO:\w+\]|tcp):\/\/\[HOST\]:(\[PORT:\d+\]|\d+).*$"
        ),
        vol.Optional(
            ATTR_WATCHDOG_RESTART_POLICY, default=WatchdogRestartPolicy.RATE_LIMITED
        ): vol.Coerce(WatchdogRestartPolicy),
        vol.Optional(ATTR_WEBUI): vol.Match(
            r"^(?:https?|\[PROTO:\w+\]):\/\/\[HOST\]:\[PORT:\d+\].*$"
        ),
        vol.Optional(ATTR_INGRESS, default=False): vol.Boolean(),
        vol.Optional(ATTR_INGRESS_PORT, default=8099): vol.Any(
            network_port, vol.Equal(0)
        ),
        vol.Optional(ATTR_INGRESS_ENTRY): str,
        vol.Optional(ATTR_INGRESS_STREAM, default=False): vol.Boolean(),
        vol.Optional(ATTR_PANEL_ICON, default="mdi:puzzle"): str,
        vol.Optional(ATTR_PANEL_TITLE): str,
        vol.Optional(ATTR_PANEL_ADMIN, default=True): vol.Boolean(),
        vol.Optional(ATTR_HOMEASSISTANT): version_tag,
        vol.Optional(ATTR_HOST_NETWORK, default=False): vol.Boolean(),
        vol.Optional(ATTR_HOST_PID, default=False): vol.Boolean(),
        vol.Optional(ATTR_HOST_IPC, default=False): vol.Boolean(),
        vol.Optional(ATTR_HOST_UTS, default=False): vol.Boolean(),
        vol.Optional(ATTR_HOST_DBUS, default=False): vol.Boolean(),
        vol.Optional(ATTR_DEVICES): [str],
        vol.Optional(ATTR_UDEV, default=False): vol.Boolean(),
        vol.Optional(ATTR_TMPFS, default=False): vol.Boolean(),
        vol.Optional(ATTR_MAP, default=list): [
            vol.Schema(
                {
                    vol.Required(ATTR_TYPE): vol.Coerce(MappingType),
                    vol.Optional(ATTR_READ_ONLY, default=True): bool,
                    vol.Optional(ATTR_PATH): str,
                }
            )
        ],
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
        vol.Optional(ATTR_DISCOVERY): [str],
        vol.Optional(ATTR_BACKUP_EXCLUDE): [str],
        vol.Optional(ATTR_BACKUP_PRE): str,
        vol.Optional(ATTR_BACKUP_POST): str,
        vol.Optional(ATTR_BACKUP, default=AppBackupMode.HOT): vol.Coerce(AppBackupMode),
        vol.Optional(ATTR_OPTIONS, default={}): dict,
        vol.Optional(ATTR_SCHEMA, default={}): vol.Any(
            vol.Schema({str: SCHEMA_ELEMENT}),
            False,
        ),
        vol.Optional(ATTR_IMAGE): docker_image,
        vol.Optional(ATTR_ULIMITS, default=dict): vol.Any(
            {str: vol.Coerce(int)},  # Simple format: {name: limit}
            {
                str: vol.Any(
                    vol.Coerce(int),  # Simple format for individual entries
                    vol.Schema(
                        {  # Detailed format for individual entries
                            vol.Required("soft"): vol.Coerce(int),
                            vol.Required("hard"): vol.Coerce(int),
                        }
                    ),
                )
            },
        ),
        vol.Optional(ATTR_TIMEOUT, default=10): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=300)
        ),
        vol.Optional(ATTR_JOURNALD, default=False): vol.Boolean(),
        vol.Optional(ATTR_BREAKING_VERSIONS, default=list): [version_tag],
    },
    extra=vol.REMOVE_EXTRA,
)


def _build_app_config_schema(log: Callable[..., None]):
    """Build the store app config schema, routing advisories through log."""
    return vol.All(_migrate_app_config(log), _warn_app_config(log), _SCHEMA_APP_CONFIG)


# Store app configs are validated on every store reload for every app in every
# repository, including ones the user has not installed. The advisories they
# raise are only actionable for a local app's author or a developer testing on
# the dev channel, so the store data layer validates with the verbose schema
# only in those cases and uses the quiet (debug-level) schema otherwise, to keep
# them out of regular users' logs.
SCHEMA_APP_CONFIG = _build_app_config_schema(_LOGGER.warning)
SCHEMA_APP_CONFIG_QUIET = _build_app_config_schema(_LOGGER.debug)


# pylint: disable=no-value-for-parameter
SCHEMA_BUILD_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_BUILD_FROM, default=dict): vol.Any(
            vol.Match(RE_DOCKER_IMAGE_BUILD),
            vol.Schema({vol.In(ARCH_ALL_COMPAT): vol.Match(RE_DOCKER_IMAGE_BUILD)}),
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
        vol.Optional(ATTR_FIELDS): {str: vol.Self},
    },
    extra=vol.REMOVE_EXTRA,
)


SCHEMA_APP_TRANSLATIONS = vol.Schema(
    {
        vol.Optional(ATTR_CONFIGURATION): {str: SCHEMA_TRANSLATION_CONFIGURATION},
        vol.Optional(ATTR_NETWORK): {str: str},
    },
    extra=vol.REMOVE_EXTRA,
)


# pylint: disable=no-value-for-parameter
SCHEMA_APP_USER = vol.Schema(
    {
        vol.Required(ATTR_VERSION): version_tag,
        vol.Optional(ATTR_IMAGE): docker_image,
        vol.Optional(ATTR_UUID, default=lambda: uuid.uuid4().hex): uuid_match,
        vol.Optional(ATTR_ACCESS_TOKEN): token,
        vol.Optional(ATTR_INGRESS_TOKEN, default=secrets.token_urlsafe): str,
        vol.Optional(ATTR_OPTIONS, default=dict): dict,
        vol.Optional(ATTR_AUTO_UPDATE, default=False): vol.Boolean(),
        vol.Optional(ATTR_BOOT): vol.Coerce(AppBoot),
        vol.Optional(ATTR_NETWORK): docker_ports,
        vol.Optional(ATTR_AUDIO_OUTPUT): vol.Maybe(str),
        vol.Optional(ATTR_AUDIO_INPUT): vol.Maybe(str),
        vol.Optional(ATTR_PROTECTED, default=True): vol.Boolean(),
        vol.Optional(ATTR_INGRESS_PANEL, default=False): vol.Boolean(),
        vol.Optional(ATTR_WATCHDOG, default=False): vol.Boolean(),
        vol.Optional(ATTR_SYSTEM_MANAGED, default=False): vol.Boolean(),
        vol.Optional(ATTR_SYSTEM_MANAGED_CONFIG_ENTRY, default=None): vol.Maybe(str),
    },
    extra=vol.REMOVE_EXTRA,
)

SCHEMA_APP_SYSTEM = vol.All(
    # Installed app config is re-validated from apps.json on every startup. It
    # was already migrated (and any advisory logged) when read from the store,
    # so keep these at debug level to avoid repeating them on each boot.
    _migrate_app_config(_LOGGER.debug),
    _SCHEMA_APP_CONFIG.extend(
        {
            # The source location is owned by the store and resolved at runtime
            # (see App.path_location); it is intentionally not persisted here.
            # REMOVE_EXTRA drops any stale value left in older apps.json files.
            vol.Required(ATTR_REPOSITORY): str,
            vol.Required(ATTR_TRANSLATIONS, default=dict): {
                str: SCHEMA_APP_TRANSLATIONS
            },
        }
    ),
)


SCHEMA_APPS_FILE = vol.Schema(
    {
        vol.Optional(ATTR_USER, default=dict): {str: SCHEMA_APP_USER},
        vol.Optional(ATTR_SYSTEM, default=dict): {str: SCHEMA_APP_SYSTEM},
    },
    extra=vol.REMOVE_EXTRA,
)


SCHEMA_APP_BACKUP = vol.Schema(
    {
        vol.Required(ATTR_USER): SCHEMA_APP_USER,
        vol.Required(ATTR_SYSTEM): SCHEMA_APP_SYSTEM,
        vol.Required(ATTR_STATE): vol.Coerce(AppState),
        vol.Required(ATTR_VERSION): version_tag,
    },
    extra=vol.REMOVE_EXTRA,
)
