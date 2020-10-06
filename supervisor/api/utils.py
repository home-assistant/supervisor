"""Init file for Supervisor util for RESTful API."""
import json
from typing import Any, Dict, List, Optional

from aiohttp import web
from aiohttp.hdrs import AUTHORIZATION
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..const import (
    CONTENT_TYPE_BINARY,
    HEADER_TOKEN,
    HEADER_TOKEN_OLD,
    JSON_DATA,
    JSON_MESSAGE,
    JSON_RESULT,
    RESULT_ERROR,
    RESULT_OK,
)
from ..exceptions import (
    APIError,
    APIForbidden,
    DockerAPIError,
    DockerRequestError,
    HassioError,
)
from ..utils import check_exception_chain
from ..utils.log_format import format_message


def excract_supervisor_token(request: web.Request) -> Optional[str]:
    """Extract Supervisor token from request."""
    supervisor_token = request.headers.get(HEADER_TOKEN)
    if supervisor_token:
        return supervisor_token

    # Remove with old Supervisor fallback
    supervisor_token = request.headers.get(HEADER_TOKEN_OLD)
    if supervisor_token:
        return supervisor_token

    # API access only
    supervisor_token = request.headers.get(AUTHORIZATION)
    if supervisor_token:
        return supervisor_token.split(" ")[-1]

    return None


def json_loads(data: Any) -> Dict[str, Any]:
    """Extract json from string with support for '' and None."""
    if not data:
        return {}
    try:
        return json.loads(data)
    except json.JSONDecodeError as err:
        raise APIError("Invalid json") from err


def api_process(method):
    """Wrap function with true/false calls to rest api."""

    async def wrap_api(api, *args, **kwargs):
        """Return API information."""
        try:
            answer = await method(api, *args, **kwargs)
        except (APIError, APIForbidden, HassioError) as err:
            return api_return_error(error=err)

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
            except (APIError, APIForbidden) as err:
                msg_data = str(err).encode()
                msg_type = CONTENT_TYPE_BINARY
            except HassioError:
                msg_data = b""
                msg_type = CONTENT_TYPE_BINARY

            return web.Response(body=msg_data, content_type=msg_type)

        return wrap_api

    return wrap_method


def api_return_error(error: Optional[Any] = None) -> web.Response:
    """Return an API error message."""
    message = str(error)
    if check_exception_chain(error, (DockerRequestError, DockerAPIError)):
        message = format_message(message)
    return web.json_response(
        {
            JSON_RESULT: RESULT_ERROR,
            JSON_MESSAGE: message or "Unknown error, see supervisor logs",
        },
        status=400,
    )


def api_return_ok(data: Optional[Dict[str, Any]] = None) -> web.Response:
    """Return an API ok answer."""
    return web.json_response({JSON_RESULT: RESULT_OK, JSON_DATA: data or {}})


async def api_validate(
    schema: vol.Schema, request: web.Request, origin: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Validate request data with schema."""
    data: Dict[str, Any] = await request.json(loads=json_loads)
    try:
        data_validated = schema(data)
    except vol.Invalid as ex:
        raise APIError(humanize_error(data, ex)) from None

    if not origin:
        return data_validated

    for origin_value in origin:
        if origin_value not in data_validated:
            continue
        data_validated[origin_value] = data[origin_value]

    return data_validated
