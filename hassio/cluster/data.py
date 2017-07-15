"""Init file for HassIO cluster."""
import logging

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .validate import SCHEMA_CLUSTER_CONFIG
from ..const import FILE_HASSIO_CLUSTER, ATTR_NODE, ATTR_NODES
from ..tools import JsonConfig

_LOGGER = logging.getLogger(__name__)


class ClusterData(JsonConfig):
    """Hold data for addons inside HassIO."""

    def __init__(self):
        """Initialize data holder."""
        super().__init__(FILE_HASSIO_CLUSTER, SCHEMA_CLUSTER_CONFIG)

    @property
    def initialize(self):
        """Return true if cluster is initialize."""
        return bool(self._data[ATTR_NODE])

    @property
    def node(self):
        """Return data of own node."""
        return self._data[ATTR_NODE]

    @property
    def nodes(self):
        """Return dict of nodes."""
        return self._data[ATTR_NODES]
