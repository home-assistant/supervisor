"""Init file for HassIO util for cluster."""

import random
import string

from ..api.util import hash_password
from ..const import HASSIO_PUBLIC_CLUSTER_PORT, HTTP_HEADER_X_NODE_KEY


def generate_cluster_key():
    """Generating random key (master/node)."""
    return "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(8))


def get_node_slug(node_name):
    """Fixing node name."""
    return node_name.replace(" ", "_")


def get_public_cluster_url(ip_address, relative_url):
    """Preparing URL for public cluster API."""
    if relative_url[0] != "/":
        relative_url = "/" + relative_url
    return "http://{0}:{1}/" \
           "cluster/public{2}".format(ip_address,
                                      HASSIO_PUBLIC_CLUSTER_PORT,
                                      relative_url)


def get_security_headers_raw(hash_key):
    """Returning security header using hashed node key."""
    return {
        HTTP_HEADER_X_NODE_KEY: hash_key
    }


def get_security_headers(cluster):
    """Returning security header using config."""
    return get_security_headers_raw(hash_password(cluster.node_key))
