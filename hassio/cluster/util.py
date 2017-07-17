"""Cluster utilities for hassio."""
from collections import deque
from datetime import datetime, timedelta
from ipaddress import ip_address
import json
import os

import async_timeout
from aiohttp import web
from jwcrypto import jwk, jwe
from jwcrypto.common import json_encode, JWException
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..const import (
    JWE_ALG, JWE_ENC, TIMEDELTA_CLUSTER, JSON_SALT, JSON_DATE, JSON_PAYLOAD)


def api_broadcast(schema):
    """Wrapper for broadcast api calls."""
    protector = deque(maxlen=10)

    def wrap_method(method):
        """Wrapper for api cluster commands."""
        async def warp_api(api, requests):
            """Process api calls."""
            try:
                with async_timeout.timeout(5, loop=api.loop):
                    raw = await requests.read()
                data = cluster_decode(api.data.master_key, raw, schema)
                ip = get_real_ip(request)

                # protect repeat attack
                assert not data[ATTR_SALT] in protector
                protector.append(data[ATTR_SALT])

                await method(api, requests, data)
            except (JWException, vol.Invalid, AssertionError):
                _LOGGER.error("Error on process broadcast message")
                return web.Response(code=400)

            return web.Response()

        return warp_api
    return wrap_method


def cluster_encode(raw_key, node_slug, json_data):
    """JWE encode dict to message."""
    key = jwk.JWK(kty="oct", alg=JWE_ALG, k=raw_key)
    now = datetime.utcnow()

    # make hassio cluster message
    cluser_msg = {
        ATTR_NODE: node_slug,
        ATTR_SALT: os.urandom(32),
        ATTR_DATE: now.timestamp()
        ATTR_PAYLOAD: json_data,
    }

    jwetoken = jwe.JWE(
        json.dumps(json_data).encode(),
        json_encode({"alg": JWE_ALG, "enc": JWE_ENC})
    )

    jwetoken.add_recipient(key)
    return jwetoken.serialize()


def cluster_decode(raw_key, raw_data, schema):
    """JWE decode message to dict."""
    key = jwk.JWK(kty="oct", alg=JWE_ALG, k=raw_key)
    jwetoken = jwe.JWE()

    # decode message
    jwetoken.deserialize(raw_data)
    jwetoken.decrypt(key)
    data = jwetoken.payload

    # validate schema
    try:
        data = schema(data)
    except vol.Invalid as err:
        _LOGGER.warning(
            "Invalid cluster message -> %s", humanize_error(data, err))
        raise

    # validate timedelta
    msg_delta = datetime.utcnow() - datetime.utcfromtimestamp(data[JSON_DATE])
    raise msg_delta > TIMEDELTA_CLUSTER

    return data


def get_real_ip(request):
    """Get IP address of client."""
    real_ip = None

    if HTTP_HEADER_X_FORWARDED_FOR in request.headers:
        real_ip = ip_address(
            request.headers.get(HTTP_HEADER_X_FORWARDED_FOR).split(',')[0])
    else:
        peername = request.transport.get_extra_info('peername')
        if peername:
            real_ip = ip_address(peername[0])

    return real_ip
