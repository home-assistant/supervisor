"""Init file for Supervisor Observer RESTful API."""

import logging
from typing import Any

from ..const import ATTR_HOST
from ..plugins.observer import PluginObserver
from .plugins import APIPlugin

_LOGGER: logging.Logger = logging.getLogger(__name__)


class APIObserver(APIPlugin[PluginObserver]):
    """Handle RESTful API for Observer functions."""

    def _info(self) -> dict[str, Any]:
        """Return HA Observer information."""
        return super()._info() | {
            ATTR_HOST: str(self.sys_docker.network.observer),
        }
