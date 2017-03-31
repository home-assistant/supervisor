"""Init file for HassIO util for rest api."""
import logging

from aiohttp import web
from aiohttp.web_exceptions import HTTPServiceUnavailable

from ..const import (
    JSON_RESULT, JSON_DATA, JSON_MESSAGE, RESULT_OK, RESULT_ERROR)

_LOGGER = logging.getLogger(__name__)


def api_process_hostcontroll(method):
    """Wrap HostControll calls to rest api."""
    async def wrap_hostcontroll(api, *args, **kwargs):
        """Return host information."""
        if not api.host_controll.active:
            raise HTTPServiceUnavailable()

        answer = await method(api, *args, **kwargs)
        if isinstance(answer, dict):
            return web.json_response(answer)
        elif answer is None:
            return api_not_supported()
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


def api_return_ok(data=None):
    """Return a API ok answer."""
    return web.json_response({
        JSON_RESULT: RESULT_OK,
        JSON_DATA: data,
    })


def api_not_supported():
    """Return a api error with not supported."""
    return api_return_error("Function is not supported")
