"""Init file for HassIO util for cluster."""

import json
import logging
import hashlib

from aiohttp import web
from jwcrypto import jwk, jwe
from jwcrypto.common import json_encode

from ..const import JSON_RESULT, RESULT_OK

_LOGGER = logging.getLogger(__name__)

KEY_TYPE = "A128KW"
ENC_ALG = "A128CBC-HS256"


def generate_cluster_key():
    """Generating random key (master/node)."""
    key = jwk.JWK.generate(kty="oct", alg=KEY_TYPE)
    export = json.loads(key.export_symmetric())
    return export["k"]


def get_node_slug(node_name):
    """Fixing node name."""
    return hashlib.sha1(node_name.encode()).hexdigest()[:8]


def get_key(key):
    """Wrapping encryption key."""
    return jwk.JWK(kty="oct", alg=KEY_TYPE, k=key)


def cluster_decrypt(data, plain_key):
    """Decrypting data."""
    key = get_key(plain_key)
    token = jwe.JWE()
    token.deserialize(data, key=key)
    return token.payload.decode("utf-8")


async def cluster_decrypt_body(request, plain_key):
    """Decrypting request/response body."""
    enc_body = await request.text()
    return cluster_decrypt(enc_body, plain_key)


async def cluster_decrypt_body_json(request, plain_key):
    """Decrypting request/response body into JSON object."""
    body = await cluster_decrypt_body(request, plain_key)
    return json.loads(body)


async def cluster_decrypt_schema(schema, request, plain_key):
    """Decrypting request/response body with schema validation."""
    return schema(await cluster_decrypt_body_json(request, plain_key))


def cluster_public_api_process(method):
    """Wrapping every possible error."""

    async def wrap_api(api, *args, **kwargs):
        """Return api information."""
        try:
            result = await method(api, *args, **kwargs)
            return web.Response(body=result)
        # pylint: disable=broad-except
        except Exception as err:
            _LOGGER.error("Cluster API invocation error: %s", str(err))
            return web.Response(status=400)

    return wrap_api


def cluster_encrypt(data, plain_key):
    """Encrypting plain data."""
    key = get_key(plain_key)
    token = jwe.JWE(data.encode("utf-8"),
                    json_encode({
                        "alg": KEY_TYPE,
                        "enc": ENC_ALG
                    }))
    token.add_recipient(key)
    return token.serialize(compact=True)


def cluster_encrypt_json(json_data, plain_key):
    """Encrypting object as JSON."""
    return cluster_encrypt(json.dumps(json_data), plain_key)


def cluster_encrypt_ok(plain_key):
    """Default OK response inside cluster."""
    return cluster_encrypt_json({
        JSON_RESULT: RESULT_OK
    }, plain_key)
