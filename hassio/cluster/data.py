"""Init file for HassIO cluster."""
import logging

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .validate import SCHEMA_CLUSTER_CONFIG
from ..const import (
    FILE_HASSIO_CLUSTER, ATTR_NODE, ATTR_NODES, ATTR_MASTER_KEY, ATTR_LEVEL,
    ATTR_SLUG, ATTR_NAME)
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
    def master_key(self):
        """Return master key of cluster."""
        return self._data[ATTR_NODE].get(ATTR_MASTER_KEY)

    @master_key.setter
    def master_key(self, value):
        """Set master key of cluster."""
        if self.master_key:
            return
        self._data[ATTR_NODE][ATTR_MASTER_KEY] = value

    @property
    def level(self):
        """Return level of cluster."""
        return self._data[ATTR_NODE].get(ATTR_LEVEL)

    @level.setter
    def level(self, value):
        """Set level of cluster."""
        self._data[ATTR_NODE][ATTR_LEVEL] = value

    @property
    def node_slug(self):
        """Return slug of this node."""
        return self._data[ATTR_NODE].get(ATTR_SLUG)

    @node_slug.setter
    def node_slug(self, value):
        """Set slug of this node."""
        self._data[ATTR_NODE][ATTR_SLUG] = value

    @property
    def node_name(self):
        """Return name of this node."""
        return self._data[ATTR_NODE].get(ATTR_NAME)

    @node_name.setter
    def node_name(self, value):
        """Return name of this node."""
        self._data[ATTR_NODE][ATTR_NAME] = value

    @property
    def nodes(self):
        """Return dict of nodes."""
        return self._data[ATTR_NODES]
