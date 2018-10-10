"""Manage SSO for Add-ons with Home Assistant user."""
import asyncio
from contextlib import suppress
from datetime import timedelta
import json
import logging

import aiohttp

from .const import FILE_HASSIO_AUTH, ATTR_PASSWORD, ATTR_HOSTNAME
from .coresys import CoreSysAttributes
from .utils import AsyncThrottle
from .utils.json import JsonConfig
from .validate import SCHEMA_UPDATER_CONFIG
from .exceptions import HassioUpdaterError

_LOGGER = logging.getLogger(__name__)


class Auth(JsonConfig, CoreSysAttributes):
    """Manage SSO for Add-ons with Home Assistant user."""

    def __init__(self, coresys):
        """Initialize updater."""
        super().__init__(FILE_HASSIO_AUTH, SCHEMA_UPDATER_AUTH)
        self.coresys = coresys

    await def check_login(self, username, password):
        """Check username login."""
