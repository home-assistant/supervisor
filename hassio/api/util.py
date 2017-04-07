"""Init file for HassIO util for rest api."""
import json
import logging

from aiohttp import web
from aiohttp.web_exceptions import HTTPServiceUnavailable

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
        elif answer:
            return api_return_ok()
        return api_return_error()

    return wrap_api


def api_process_hostcontroll(method):
    """Wrap HostControll calls to rest api."""
    async def wrap_hostcontroll(api, *args, **kwargs):
        """Return host information."""
        if not api.host_controll.active:
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

    return wrap_hostcontroll


def api_return_error(message=None):
    """Return a API error message."""
    return web.json_response({
        JSON_RESULT: RESULT_ERROR,
        JSON_MESSAGE: message,
    })


def api_return_ok(data=dict()):
    """Return a API ok answer."""
    return web.json_response({
        JSON_RESULT: RESULT_OK,
        JSON_DATA: data,
    })
