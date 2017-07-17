"""Handle a single HassIO node."""
from datetime import datetime

from ..const import ATTR_IP, ATTR_NAME, ATTR_LAST_SEEN


class ClusterNode(object):
    """Handle a cluser node."""

    def __ini__(self, data, slug):
        """Initialze a node."""
        self.data = data
        self._id = slug

    @property
    def slug(self):
        """Get slug of node."""
        return self._id

    @property
    def ip(self):
        """Get IP address."""
        return self.data.nodes[self._id][ATTR_IP]

    @ip.setter
    def ip(self, value):
        """Set IP address."""
        self.data.nodes[self._id][ATTR_IP] = value

    @property
    def name(self):
        """Get name of node."""
        return self.data.nodes[self._id][ATTR_NAME]

    @name.setter
    def name(self, value):
        """Set name of node."""
        self.data.nodes[self._id][ATTR_NAME] = value
