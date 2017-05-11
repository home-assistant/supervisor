"""Init file for HassIO util for rest api."""
import json
import hashlib
import logging

from aiohttp import web
from aiohttp.web_exceptions import HTTPServiceUnavailable
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..const import (
    JSON_RESULT, JSON_DATA, JSON_MESSAGE, RESULT_OK, RESULT_ERROR)

_LOGGER = logging.getLogger(__name__)


def json_loads(data):
    """Extract json from string with support for '' and None."""
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return {}


def api_process(method):
    """Wrap function with true/false calls to rest api."""
    async def wrap_api(api, *args, **kwargs):
        """Return api information."""
        try:
            answer = await method(api, *args, **kwargs)
        except RuntimeError as err:
            return api_return_error(message=str(err))

        if isinstance(answer, dict):
            return api_return_ok(data=answer)
        if isinstance(answer, web.Response):
            return answer
        elif answer:
            return api_return_ok()
        return api_return_error()

    return wrap_api


def api_process_hostcontrol(method):
    """Wrap HostControl calls to rest api."""
    async def wrap_hostcontrol(api, *args, **kwargs):
        """Return host information."""
        if not api.host_control.active:
            raise HTTPServiceUnavailable()

        try:
            answer = await method(api, *args, **kwargs)
        except RuntimeError as err:
            return api_return_error(message=str(err))

        if isinstance(answer, dict):
            return api_return_ok(data=answer)
        elif answer is None:
            return api_return_error("Function is not supported")
        elif answer:
            return api_return_ok()
        return api_return_error()

    return wrap_hostcontrol


def api_process_raw(method):
    """Wrap function with raw output to rest api."""
    async def wrap_api(api, *args, **kwargs):
        """Return api information."""
        try:
            message = await method(api, *args, **kwargs)
        except RuntimeError as err:
            message = str(err).encode()

        return web.Response(body=message)

    return wrap_api


def api_return_error(message=None):
    """Return a API error message."""
    return web.json_response({
        JSON_RESULT: RESULT_ERROR,
        JSON_MESSAGE: message,
    }, status=400)


def api_return_ok(data=None):
    """Return a API ok answer."""
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
