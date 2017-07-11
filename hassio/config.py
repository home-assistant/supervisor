"""Bootstrap HassIO."""
from datetime import datetime
import logging
import os
from pathlib import Path, PurePath

import voluptuous as vol

from .const import FILE_HASSIO_CONFIG, HASSIO_DATA
from .tools import fetch_last_versions, JsonConfig, validate_timezone

_LOGGER = logging.getLogger(__name__)

DATETIME_FORMAT = "%Y%m%d %H:%M:%S"

HOMEASSISTANT_CONFIG = PurePath("homeassistant")
HOMEASSISTANT_LAST = 'homeassistant_last'

HASSIO_SSL = PurePath("ssl")
HASSIO_LAST = 'hassio_last'

ADDONS_CORE = PurePath("addons/core")
ADDONS_LOCAL = PurePath("addons/local")
ADDONS_GIT = PurePath("addons/git")
ADDONS_DATA = PurePath("addons/data")
ADDONS_CUSTOM_LIST = 'addons_custom_list'

BACKUP_DATA = PurePath("backup")
SHARE_DATA = PurePath("share")
TMP_DATA = PurePath("tmp")

UPSTREAM_BETA = 'upstream_beta'
API_ENDPOINT = 'api_endpoint'
TIMEZONE = 'timezone'

SECURITY_INITIALIZE = 'security_initialize'
SECURITY_TOTP = 'security_totp'
SECURITY_PASSWORD = 'security_password'
SECURITY_SESSIONS = 'security_sessions'

CLUSTER_IS_MASTER = 'is_master'
CLUSTER_MASTER_IP = 'master_ip'
CLUSTER_NODE_KEY = 'node_key'
CLUSTER_KNOWN_NODES = 'known_nodes'
CLUSTER_NODE_NAME = 'node_name'

# pylint: disable=no-value-for-parameter
SCHEMA_CONFIG = vol.Schema({
    vol.Optional(UPSTREAM_BETA, default=False): vol.Boolean(),
    vol.Optional(API_ENDPOINT): vol.Coerce(str),
    vol.Optional(TIMEZONE, default='UTC'): validate_timezone,
    vol.Optional(HOMEASSISTANT_LAST): vol.Coerce(str),
    vol.Optional(HASSIO_LAST): vol.Coerce(str),
    vol.Optional(ADDONS_CUSTOM_LIST, default=[]): [vol.Url()],
    vol.Optional(SECURITY_INITIALIZE, default=False): vol.Boolean(),
    vol.Optional(SECURITY_TOTP): vol.Coerce(str),
    vol.Optional(SECURITY_PASSWORD): vol.Coerce(str),
    vol.Optional(SECURITY_SESSIONS, default={}):
        {vol.Coerce(str): vol.Coerce(str)},
    vol.Optional(CLUSTER_IS_MASTER, default=True): vol.Boolean(),
    vol.Optional(CLUSTER_MASTER_IP, default=""): vol.Coerce(str),
    vol.Optional(CLUSTER_NODE_KEY, default=""): vol.Coerce(str),
    vol.Optional(CLUSTER_NODE_NAME, default=""): vol.Coerce(str),
    vol.Optional(CLUSTER_KNOWN_NODES, default={}):
        {vol.Coerce(str): vol.Coerce(str)},
}, extra=vol.REMOVE_EXTRA)


class CoreConfig(JsonConfig):
    """Hold all core config data."""

    def __init__(self):
        """Initialize config object."""
        super().__init__(FILE_HASSIO_CONFIG, SCHEMA_CONFIG)
        self.arch = None

    async def fetch_update_infos(self, websession):
        """Read current versions from web."""
        last = await fetch_last_versions(websession, beta=self.upstream_beta)

        if last:
            self._data.update({
                HOMEASSISTANT_LAST: last.get('homeassistant'),
                HASSIO_LAST: last.get('hassio'),
            })
            self.save()
            return True

        return False

    @property
    def api_endpoint(self):
        """Return IP address of api endpoint."""
        return self._data[API_ENDPOINT]

    @api_endpoint.setter
    def api_endpoint(self, value):
        """Store IP address of api endpoint."""
        self._data[API_ENDPOINT] = value

    @property
    def upstream_beta(self):
        """Return True if we run in beta upstream."""
        return self._data[UPSTREAM_BETA]

    @upstream_beta.setter
    def upstream_beta(self, value):
        """Set beta upstream mode."""
        self._data[UPSTREAM_BETA] = bool(value)
        self.save()

    @property
    def timezone(self):
        """Return system timezone."""
        return self._data[TIMEZONE]

    @timezone.setter
    def timezone(self, value):
        """Set system timezone."""
        self._data[TIMEZONE] = value
        self.save()

    @property
    def last_homeassistant(self):
        """Actual version of homeassistant."""
        return self._data.get(HOMEASSISTANT_LAST)

    @property
    def last_hassio(self):
        """Actual version of hassio."""
        return self._data.get(HASSIO_LAST)

    @property
    def path_hassio(self):
        """Return hassio data path."""
        return HASSIO_DATA

    @property
    def path_extern_hassio(self):
        """Return hassio data path extern for docker."""
        return PurePath(os.environ['SUPERVISOR_SHARE'])

    @property
    def path_extern_config(self):
        """Return config path extern for docker."""
        return str(PurePath(self.path_extern_hassio, HOMEASSISTANT_CONFIG))

    @property
    def path_config(self):
        """Return config path inside supervisor."""
        return Path(HASSIO_DATA, HOMEASSISTANT_CONFIG)

    @property
    def path_extern_ssl(self):
        """Return SSL path extern for docker."""
        return str(PurePath(self.path_extern_hassio, HASSIO_SSL))

    @property
    def path_ssl(self):
        """Return SSL path inside supervisor."""
        return Path(HASSIO_DATA, HASSIO_SSL)

    @property
    def path_addons_core(self):
        """Return git path for core addons."""
        return Path(HASSIO_DATA, ADDONS_CORE)

    @property
    def path_addons_git(self):
        """Return path for git addons."""
        return Path(HASSIO_DATA, ADDONS_GIT)

    @property
    def path_addons_local(self):
        """Return path for customs addons."""
        return Path(HASSIO_DATA, ADDONS_LOCAL)

    @property
    def path_extern_addons_local(self):
        """Return path for customs addons."""
        return PurePath(self.path_extern_hassio, ADDONS_LOCAL)

    @property
    def path_addons_data(self):
        """Return root addon data folder."""
        return Path(HASSIO_DATA, ADDONS_DATA)

    @property
    def path_extern_addons_data(self):
        """Return root addon data folder extern for docker."""
        return PurePath(self.path_extern_hassio, ADDONS_DATA)

    @property
    def path_tmp(self):
        """Return hass.io temp folder."""
        return Path(HASSIO_DATA, TMP_DATA)

    @property
    def path_backup(self):
        """Return root backup data folder."""
        return Path(HASSIO_DATA, BACKUP_DATA)

    @property
    def path_extern_backup(self):
        """Return root backup data folder extern for docker."""
        return PurePath(self.path_extern_hassio, BACKUP_DATA)

    @property
    def path_share(self):
        """Return root share data folder."""
        return Path(HASSIO_DATA, SHARE_DATA)

    @property
    def path_extern_share(self):
        """Return root share data folder extern for docker."""
        return PurePath(self.path_extern_hassio, SHARE_DATA)

    @property
    def addons_repositories(self):
        """Return list of addons custom repositories."""
        return self._data[ADDONS_CUSTOM_LIST]

    @addons_repositories.setter
    def addons_repositories(self, repo):
        """Add a custom repository to list."""
        if repo in self._data[ADDONS_CUSTOM_LIST]:
            return

        self._data[ADDONS_CUSTOM_LIST].append(repo)
        self.save()

    def drop_addon_repository(self, repo):
        """Remove a custom repository from list."""
        if repo not in self._data[ADDONS_CUSTOM_LIST]:
            return

        self._data[ADDONS_CUSTOM_LIST].remove(repo)
        self.save()

    @property
    def security_initialize(self):
        """Return is security was initialize."""
        return self._data[SECURITY_INITIALIZE]

    @security_initialize.setter
    def security_initialize(self, value):
        """Set is security initialize."""
        self._data[SECURITY_INITIALIZE] = value
        self.save()

    @property
    def security_totp(self):
        """Return the TOTP key."""
        return self._data.get(SECURITY_TOTP)

    @security_totp.setter
    def security_totp(self, value):
        """Set the TOTP key."""
        self._data[SECURITY_TOTP] = value
        self.save()

    @property
    def security_password(self):
        """Return the password key."""
        return self._data.get(SECURITY_PASSWORD)

    @security_password.setter
    def security_password(self, value):
        """Set the password key."""
        self._data[SECURITY_PASSWORD] = value
        self.save()

    @property
    def security_sessions(self):
        """Return api sessions."""
        return {session: datetime.strptime(until, DATETIME_FORMAT) for
                session, until in self._data[SECURITY_SESSIONS].items()}

    @security_sessions.setter
    def security_sessions(self, value):
        """Set the a new session."""
        session, valid = value
        if valid is None:
            self._data[SECURITY_SESSIONS].pop(session, None)
        else:
            self._data[SECURITY_SESSIONS].update(
                {session: valid.strftime(DATETIME_FORMAT)}
            )

        self.save()

    @property
    def is_master(self):
        """Return flag indicating whether this node operates as master."""
        return self._data.get(CLUSTER_IS_MASTER)

    @is_master.setter
    def is_master(self, value):
        """Set operation mode."""
        self._data[CLUSTER_IS_MASTER] = value
        self.save()

    @property
    def master_ip(self):
        """Return master IP address."""
        return self._data.get(CLUSTER_MASTER_IP)

    @master_ip.setter
    def master_ip(self, value):
        """Set master IP address."""
        self._data[CLUSTER_MASTER_IP] = value
        self.save()

    @property
    def node_key(self):
        """Return node secret key."""
        return self._data.get(CLUSTER_NODE_KEY)

    @node_key.setter
    def node_key(self, value):
        """Set node secret key."""
        self._data[CLUSTER_NODE_KEY] = value
        self.save()

    @property
    def known_nodes(self):
        """Return information about known nodes."""
        return self._data[CLUSTER_KNOWN_NODES]

    @known_nodes.setter
    def known_nodes(self, value):
        """Set known node."""
        slug, key = value
        if key is None:
            self._data[CLUSTER_KNOWN_NODES].pop(slug, None)
        else:
            self._data[CLUSTER_KNOWN_NODES][slug] = key
        self.save()

    @property
    def node_name(self):
        """Return node name."""
        return self._data[CLUSTER_NODE_NAME]

    @node_name.setter
    def node_name(self, value):
        """Set node name."""
        self._data[CLUSTER_NODE_NAME] = value
        self.save()
