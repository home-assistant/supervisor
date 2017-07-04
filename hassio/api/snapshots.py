"""Init file for HassIO snapshot rest api."""
import logging

import voluptuous as vol

from .util import api_process, api_validate

_LOGGER = logging.getLogger(__name__)


SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_HOSTNAME): vol.Coerce(str),
})


class APISnapshots(object):
    """Handle rest api for snapshot functions."""

    def __init__(self, config, loop, snapshots):
        """Initialize network rest api part."""
        self.config = config
        self.loop = loop
        self.snapshots = snapshots
