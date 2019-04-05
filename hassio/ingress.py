"""Fetch last versions from webserver."""
from contextlib import suppress
from datetime import timedelta
import logging
from typing import Dict, Optional

from .addons.addon import Addon
from .const import (
    ATTR_CHANNEL,
    ATTR_HASSIO,
    ATTR_HASSOS,
    ATTR_HASSOS_CLI,
    ATTR_HOMEASSISTANT,
    FILE_HASSIO_INGRESS,
)
from .coresys import CoreSys, CoreSysAttributes
from .utils.json import JsonConfig
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
            return None
        return self.sys_addons.get(self.tokens[token])

    async def load(self) -> None:
        """Update internal data."""
        self._update_token_list()

    def cleanup_sessions(self):
        """Remove not used sessions."""

    def _update_token_list(self) -> None:
        """Regenerate token <-> Add-on map."""
        self.tokens.clear()

        # Read all ingress token and build a map
        for addon in self.sys_addons.list_installed:
            if not addon.with_ingress:
                continue
            self.tokens[addon.ingress_token] = addon.slug
