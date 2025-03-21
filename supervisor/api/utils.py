"""Init file for Supervisor util for RESTful API."""

import json
from typing import Any

from aiohttp import web
from aiohttp.hdrs import AUTHORIZATION
from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp.web_request import Request
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..const import (
    HEADER_TOKEN,
    HEADER_TOKEN_OLD,
    JSON_DATA,
    JSON_JOB_ID,
    JSON_MESSAGE,
    JSON_RESULT,
    REQUEST_FROM,
    RESULT_ERROR,
    RESULT_OK,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import APIError, BackupFileNotFoundError, DockerAPIError, HassioError
from ..utils import check_exception_chain, get_message_from_exception_chain
from ..utils.json import json_dumps, json_loads as json_loads_util
from ..utils.log_format import format_message
from . import const


def extract_supervisor_token(request: web.Request) -> str | None:
    """Extract Supervisor token from request."""
    if supervisor_token := request.headers.get(HEADER_TOKEN):
        return supervisor_token

    # Old Supervisor fallback
    if supervisor_token := request.headers.get(HEADER_TOKEN_OLD):
        return supervisor_token

    # API access only
    if supervisor_token := request.headers.get(AUTHORIZATION):
        return supervisor_token.split(" ")[-1]

    return None


def json_loads(data: Any) -> dict[str, Any]:
    """Extract json from string with support for '' and None."""
    if not data:
        return {}
    try:
        return json_loads_util(data)
    except json.JSONDecodeError as err:
        raise APIError("Invalid json") from err


def api_process(method):
    """Wrap function with true/false calls to rest api."""

    async def wrap_api(
        api: CoreSysAttributes, *args, **kwargs
    ) -> web.Response | web.StreamResponse:
        """Return API information."""
        try:
            answer = await method(api, *args, **kwargs)
        except BackupFileNotFoundError as err:
            return api_return_error(err, status=404)
        except APIError as err:
            return api_return_error(err, status=err.status, job_id=err.job_id)
        except HassioError as err:
            return api_return_error(err)

        if isinstance(answer, (dict, list)):
            return api_return_ok(data=answer)
        if isinstance(answer, web.Response):
            return answer
        if isinstance(answer, web.StreamResponse):
            return answer
        elif isinstance(answer, bool) and not answer:
            return api_return_error()
        return api_return_ok()

    return wrap_api


def require_home_assistant(method):
    """Ensure that the request comes from Home Assistant."""

    async def wrap_api(api: CoreSysAttributes, *args, **kwargs) -> Any:
        """Return API information."""
        coresys: CoreSys = api.coresys
        request: Request = args[0]
        if request[REQUEST_FROM] != coresys.homeassistant:
            raise HTTPUnauthorized()
        return await method(api, *args, **kwargs)

    return wrap_api


def api_process_raw(content, *, error_type=None):
    """Wrap content_type into function."""

    def wrap_method(method):
        """Wrap function with raw output to rest api."""

        async def wrap_api(
            api: CoreSysAttributes, *args, **kwargs
        ) -> web.Response | web.StreamResponse:
            """Return api information."""
            try:
                msg_data = await method(api, *args, **kwargs)
            except APIError as err:
                return api_return_error(
                    err,
                    error_type=error_type or const.CONTENT_TYPE_BINARY,
                    status=err.status,
                    job_id=err.job_id,
                )
            except HassioError as err:
                return api_return_error(
                    err, error_type=error_type or const.CONTENT_TYPE_BINARY
                )

            if isinstance(msg_data, (web.Response, web.StreamResponse)):
                return msg_data

            return web.Response(body=msg_data, content_type=content)

        return wrap_api

    return wrap_method


def api_return_error(
    error: Exception | None = None,
    message: str | None = None,
    error_type: str | None = None,
    status: int = 400,
    job_id: str | None = None,
) -> web.Response:
    """Return an API error message."""
    if error and not message:
        message = get_message_from_exception_chain(error)
        if check_exception_chain(error, DockerAPIError):
            message = format_message(message)
    if not message:
        message = "Unknown error, see supervisor"

    match error_type:
        case const.CONTENT_TYPE_TEXT:
            return web.Response(body=message, content_type=error_type, status=status)
        case const.CONTENT_TYPE_BINARY:
            return web.Response(
                body=message.encode(), content_type=error_type, status=status
            )
        case _:
            result = {
                JSON_RESULT: RESULT_ERROR,
                JSON_MESSAGE: message,
            }
            if job_id:
                result[JSON_JOB_ID] = job_id

    return web.json_response(
        result,
        status=status,
        dumps=json_dumps,
    )


def api_return_ok(data: dict[str, Any] | list[Any] | None = None) -> web.Response:
    """Return an API ok answer."""
    return web.json_response(
        {JSON_RESULT: RESULT_OK, JSON_DATA: data or {}},
        dumps=json_dumps,
    )


async def api_validate(
    schema: vol.Schema | vol.All,
    request: web.Request,
    origin: list[str] | None = None,
) -> dict[str, Any]:
    """Validate request data with schema."""
    data: dict[str, Any] = await request.json(loads=json_loads)
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
