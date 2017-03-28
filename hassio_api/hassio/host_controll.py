"""Host controll for HassIO."""
import asyncio
import logging

from .const import SOCKET_HC

_LOGGER = logging.getLogger(__name__)

class HostControll(object):
    """Manage host function."""

    def __init__(self, loop):
        """Initialize host controll."""
