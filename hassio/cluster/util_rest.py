"""Init file for HassIO REST API util for cluster."""

import logging
import time
import async_timeout

from ..const import HTTP_HEADER_X_NODE, ATTR_NONCE, HASSIO_PUBLIC_CLUSTER_PORT
from .util import (cluster_encrypt_json, cluster_decrypt_body_json,
                   cluster_decrypt_body, get_node_slug)

_LOGGER = logging.getLogger(__name__)


def get_headers(node_name):
    """Return default node headers."""
    if node_name is None:
        headers = {}
    else:
        headers = {
            HTTP_HEADER_X_NODE: get_node_slug(node_name)
        }

    return headers


def get_nonce_request():
    """Standard nonce request."""
    return {
        ATTR_NONCE: int(round(time.time() * 1000))
    }


def get_public_cluster_url(ip_address, relative_url):
    """Preparing URL for public cluster API."""
    if relative_url[0] != "/":
        relative_url = "/" + relative_url
    return "http://{0}:{1}/cluster{2}".format(
        ip_address, HASSIO_PUBLIC_CLUSTER_PORT, relative_url)


async def cluster_do_request(json_obj, node_ip, url, plain_key, websession,
                             method, is_raw, headers):
    """Making request inside cluster."""
    if json_obj is None:
        json_obj = get_nonce_request()
    try:
        full_url = get_public_cluster_url(node_ip, url)
        data = cluster_encrypt_json(json_obj, plain_key)
        with async_timeout.timeout(10, loop=websession.loop):
            async with websession.request(method, full_url, data=data,
                                          headers=headers) as response:
                if is_raw:
                    return await cluster_decrypt_body(response, plain_key)
                return await cluster_decrypt_body_json(response, plain_key)
    # pylint: disable=broad-except
    except Exception as err:
        _LOGGER.error("Failed to execute cluster call %s: %s", url, str(err))
        return None


async def cluster_do_post(json_obj, node_ip, url, plain_key, websession,
                          node_name=None, is_raw=False):
    """Performing POST request inside cluster."""
    return await cluster_do_request(json_obj, node_ip, url, plain_key,
                                    websession, "POST", is_raw,
                                    get_headers(node_name))
