"""Init file for HassIO util for rest api."""
import logging

from aiohttp import web

from ..const import (
    JSON_RESULT, JSON_DATA, JSON_MESSAGE, RESULT_OK, RESULT_ERROR)

_LOGGER = logging.getLogger(__name__)


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


def api_return_not_supported():
    """Return a api error with not supported."""
    return api_return_error("Function is not supported")
