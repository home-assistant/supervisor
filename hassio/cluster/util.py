"""Cluster utilities for hassio."""
from datetime import datetime, timedelta
import json
import os

from aiohttp import web
from aiohttp.web_exceptions import HTTPServiceUnavailable
from jwcrypto import jwk, jwe
from jwcrypto.common import json_encode
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..const import JWE_ALG, JWE_ENC, JSON_SALT, JSON_DATE, JSON_PAYLOAD


def api_cluster(method):
    """Wrapper for api cluster commands."""
    async def warp_api(api, requests):
        """Process api calls."""

    return warp_api


def cluster_encode(raw_key, node_slug, json_data):
    """JWE encode dict to message."""
    key = jwk.JWK(kty="oct", alg=JWE_ALG, k=raw_key)

    cluser_msg = {
        ATTR_NODE: node_slug,
        ATTR_SALT: os.urandom(64),
        ATTR_DATE: datetime.timestamp()
        ATTR_PAYLOAD: json_data,
    }

    jwetoken = jwe.JWE(
        json.dumps(json_data).encode(),
        json_encode({"alg": JWE_ALG, "enc": JWE_ENC})
    )

    jwetoken.add_recipient(key)
    return jwetoken.serialize()
