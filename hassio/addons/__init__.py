"""Init file for HassIO addons."""
import logging

_LOGGER = logging.getLogger(__name__)


class AddonManager(object):
    """Manage addons inside HassIO."""

    def __init__(self, config, loop):
        """Initialize docker base wrapper."""
        self.config = config
        self.loop = loop
