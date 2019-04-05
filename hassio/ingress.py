"""Fetch last versions from webserver."""
from datetime import timedelta
import logging
from typing import Dict, Optional
import secrets

from .addons.addon import Addon
from .const import ATTR_SESSION, FILE_HASSIO_INGRESS
from .coresys import CoreSys, CoreSysAttributes
from .utils.json import JsonConfig
from .utils.dt import utcnow, utc_from_timestamp
from .validate import SCHEMA_INGRESS_CONFIG

_LOGGER = logging.getLogger(__name__)


class Ingress(JsonConfig, CoreSysAttributes):
    """Fetch last versions from version.json."""

    def __init__(self, coresys: CoreSys):
        """Initialize updater."""
        super().__init__(FILE_HASSIO_INGRESS, SCHEMA_INGRESS_CONFIG)
        self.coresys: CoreSys = coresys
        self.tokens: Dict[str, str] = {}

    def get(self, token: str) -> Optional[Addon]:
        """Return addon they have this ingress token."""
        if token not in self.tokens:
            self._update_token_list()
        return self.sys_addons.get(self.tokens.get(token))

    @property
    def sessions(self) -> Dict[str, float]:
        """Return sessions."""
        return self._data[ATTR_SESSION]

    async def load(self) -> None:
        """Update internal data."""
        self._update_token_list()
        self._cleanup_sessions()

    async def reload(self) -> None:
        """Reload/Validate sessions."""
        self._cleanup_sessions()

    async def unload(self) -> None:
        """Shutdown sessions."""
        self.save_data()

    def _cleanup_sessions(self) -> None:
        """Remove not used sessions."""
        now = utcnow()

        sessions = {}
        for session, valid in self.sessions.items():
            valid_dt = utc_from_timestamp(valid)
            if valid_dt < now:
                continue

            # Is valid
            sessions[session] = valid

        # Write back
        self.sessions.clear()
        self.sessions.update(sessions)

    def _update_token_list(self) -> None:
        """Regenerate token <-> Add-on map."""
        self.tokens.clear()

        # Read all ingress token and build a map
        for addon in self.sys_addons.list_installed:
            if not addon.with_ingress:
                continue
            self.tokens[addon.ingress_token] = addon.slug

    def create_session(self) -> str:
        """Create new session."""
        session = secrets.token_hex(64)
        valid = utcnow() + timedelta(minutes=15)

        self.sessions[session] = valid.timestamp()
        self.save_data()

        return session

    def validate_session(self, session: str) -> bool:
        """Return True if session valid and make it longer valid."""
        if session not in self.sessions:
            return False
        valid_until = utc_from_timestamp(self.sessions[session])

        # Is still valid?
        if valid_until < utcnow():
            return False

        # Update time
        valid_until = valid_until + timedelta(minutes=15)
        self.sessions[session] = valid_until

        return True
