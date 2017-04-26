"""Init file for HassIO network rest api."""
import logging

from .util import api_process_hostcontrol

_LOGGER = logging.getLogger(__name__)


class APINetwork(object):
    """Handle rest api for network functions."""

    def __init__(self, config, loop, host_control):
        """Initialize network rest api part."""
        self.config = config
        self.loop = loop
        self.host_control = host_control

    @api_process_hostcontrol
    def info(self, request):
        """Show network settings."""
        pass

    @api_process_hostcontrol
    def options(self, request):
        """Edit network settings."""
        pass
