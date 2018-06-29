"""Init file for HassIO util for rest api."""
import json
import hashlib
import logging

from aiohttp import web
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..const import (
    JSON_RESULT, JSON_DATA, JSON_MESSAGE, RESULT_OK, RESULT_ERROR,
    CONTENT_TYPE_BINARY)
from ..exceptions import HassioError

_LOGGER = logging.getLogger(__name__)


def json_loads(data):
    """Extract json from string with support for '' and None."""
    if not data:
        return {}
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        raise RuntimeError("Invalid json")


def api_process(method):
    """Wrap function with true/false calls to rest api."""
    async def wrap_api(api, *args, **kwargs):
        """Return api information."""
        try:
            answer = await method(api, *args, **kwargs)
        except RuntimeError as err:
            return api_return_error(message=str(err))
        except HassioError:
            return api_return_error()

        if isinstance(answer, dict):
            return api_return_ok(data=answer)
        if isinstance(answer, web.Response):
            return answer
        elif isinstance(answer, bool) and not answer:
            return api_return_error()
        return api_return_ok()

    return wrap_api


def api_process_raw(content):
    """Wrap content_type into function."""
    def wrap_method(method):
        """Wrap function with raw output to rest api."""
        async def wrap_api(api, *args, **kwargs):
            """Return api information."""
            try:
                msg_data = await method(api, *args, **kwargs)
                msg_type = content
            except RuntimeError as err:
                msg_data = str(err).encode()
                msg_type = CONTENT_TYPE_BINARY
            except HassioError:
                msg_data = b''
                msg_type = CONTENT_TYPE_BINARY

            return web.Response(body=msg_data, content_type=msg_type)

        return wrap_api
    return wrap_method


def api_return_error(message=None):
    """Return an API error message."""
    return web.json_response({
        JSON_RESULT: RESULT_ERROR,
        JSON_MESSAGE: message,
    }, status=400)


def api_return_ok(data=None):
    """Return an API ok answer."""
    return web.json_response({
        JSON_RESULT: RESULT_OK,
        JSON_DATA: data or {},
    })


async def api_validate(schema, request):
    """Validate request data with schema."""
    data = await request.json(loads=json_loads)
    try:
        data = schema(data)
    except vol.Invalid as ex:
        raise RuntimeError(humanize_error(data, ex)) from None

    return data


def hash_password(password):
    """Hash and salt our passwords."""
    key = ")*()*SALT_HASSIO2123{}6554547485HSKA!!*JSLAfdasda$".format(password)
    return hashlib.sha256(key.encode()).hexdigest()
