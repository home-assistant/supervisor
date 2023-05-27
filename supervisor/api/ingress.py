"""Supervisor Add-on ingress service."""
import asyncio
from ipaddress import ip_address
import logging
from typing import Any

import aiohttp
from aiohttp import ClientTimeout, hdrs, web
from aiohttp.web_exceptions import (
    HTTPBadGateway,
    HTTPServiceUnavailable,
    HTTPUnauthorized,
)
from multidict import CIMultiDict, istr
import voluptuous as vol

from ..addons.addon import Addon
from ..const import (
    ATTR_ADMIN,
    ATTR_ENABLE,
    ATTR_ICON,
    ATTR_PANELS,
    ATTR_SESSION,
    ATTR_SESSION_DATA_USER_ID,
    ATTR_TITLE,
    HEADER_REMOTE_USER_DISPLAY_NAME,
    HEADER_REMOTE_USER_ID,
    HEADER_REMOTE_USER_NAME,
    HEADER_TOKEN,
    HEADER_TOKEN_OLD,
    IngressSessionData,
    IngressSessionDataUser,
)
from ..coresys import CoreSysAttributes
from ..exceptions import HomeAssistantAPIError
from .const import COOKIE_INGRESS
from .utils import api_process, api_validate, require_home_assistant

_LOGGER: logging.Logger = logging.getLogger(__name__)

VALIDATE_SESSION_DATA = vol.Schema({ATTR_SESSION: str})

"""Expected optional payload of create session request"""
SCHEMA_INGRESS_CREATE_SESSION_DATA = vol.Schema(
    {
        vol.Optional(ATTR_SESSION_DATA_USER_ID): str,
    }
)


class APIIngress(CoreSysAttributes):
    """Ingress view to handle add-on webui routing."""

    _list_of_users: list[IngressSessionDataUser]

    def __init__(self) -> None:
        """Initialize APIIngress."""
        self._list_of_users = []

    def _extract_addon(self, request: web.Request) -> Addon:
        """Return addon, throw an exception it it doesn't exist."""
        token = request.match_info.get("token")

        # Find correct add-on
        addon = self.sys_ingress.get(token)
        if not addon:
            _LOGGER.warning("Ingress for %s not available", token)
            raise HTTPServiceUnavailable()

        return addon

    def _create_url(self, addon: Addon, path: str) -> str:
        """Create URL to container."""
        return f"http://{addon.ip_address}:{addon.ingress_port}/{path}"

    @api_process
    async def panels(self, request: web.Request) -> dict[str, Any]:
        """Create a list of panel data."""
        addons = {}
        for addon in self.sys_ingress.addons:
            addons[addon.slug] = {
                ATTR_TITLE: addon.panel_title,
                ATTR_ICON: addon.panel_icon,
                ATTR_ADMIN: addon.panel_admin,
                ATTR_ENABLE: addon.ingress_panel,
            }

        return {ATTR_PANELS: addons}

    @api_process
    @require_home_assistant
    async def create_session(self, request: web.Request) -> dict[str, Any]:
        """Create a new session."""
        schema_ingress_config_session_data = await api_validate(
            SCHEMA_INGRESS_CREATE_SESSION_DATA, request
        )
        data: IngressSessionData | None = None

        if ATTR_SESSION_DATA_USER_ID in schema_ingress_config_session_data:
            user = await self._find_user_by_id(
                schema_ingress_config_session_data[ATTR_SESSION_DATA_USER_ID]
            )
            if user:
                data = IngressSessionData(user)

        session = self.sys_ingress.create_session(data)
        return {ATTR_SESSION: session}

    @api_process
    @require_home_assistant
    async def validate_session(self, request: web.Request) -> dict[str, Any]:
        """Validate session and extending how long it's valid for."""
        data = await api_validate(VALIDATE_SESSION_DATA, request)

        # Check Ingress Session
        if not self.sys_ingress.validate_session(data[ATTR_SESSION]):
            _LOGGER.warning("No valid ingress session %s", data[ATTR_SESSION])
            raise HTTPUnauthorized()

    async def handler(
        self, request: web.Request
    ) -> web.Response | web.StreamResponse | web.WebSocketResponse:
        """Route data to Supervisor ingress service."""

        # Check Ingress Session
        session = request.cookies.get(COOKIE_INGRESS)
        if not self.sys_ingress.validate_session(session):
            _LOGGER.warning("No valid ingress session %s", session)
            raise HTTPUnauthorized()

        # Process requests
        addon = self._extract_addon(request)
        path = request.match_info.get("path")
        session_data = self.sys_ingress.sessions_data[session]
        try:
            # Websocket
            if _is_websocket(request):
                return await self._handle_websocket(request, addon, path, session_data)

            # Request
            return await self._handle_request(request, addon, path, session_data)

        except aiohttp.ClientError as err:
            _LOGGER.error("Ingress error: %s", err)

        raise HTTPBadGateway()

    async def _handle_websocket(
        self,
        request: web.Request,
        addon: Addon,
        path: str,
        session_data: IngressSessionData | None,
    ) -> web.WebSocketResponse:
        """Ingress route for websocket."""
        if hdrs.SEC_WEBSOCKET_PROTOCOL in request.headers:
            req_protocols = [
                str(proto.strip())
                for proto in request.headers[hdrs.SEC_WEBSOCKET_PROTOCOL].split(",")
            ]
        else:
            req_protocols = ()

        ws_server = web.WebSocketResponse(
            protocols=req_protocols, autoclose=False, autoping=False
        )
        await ws_server.prepare(request)

        # Preparing
        url = self._create_url(addon, path)
        source_header = _init_header(request, addon, session_data)

        # Support GET query
        if request.query_string:
            url = f"{url}?{request.query_string}"

        # Start proxy
        async with self.sys_websession.ws_connect(
            url,
            headers=source_header,
            protocols=req_protocols,
            autoclose=False,
            autoping=False,
        ) as ws_client:
            # Proxy requests
            await asyncio.wait(
                [
                    self.sys_create_task(_websocket_forward(ws_server, ws_client)),
                    self.sys_create_task(_websocket_forward(ws_client, ws_server)),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

        return ws_server

    async def _handle_request(
        self,
        request: web.Request,
        addon: Addon,
        path: str,
        session_data: IngressSessionData | None,
    ) -> web.Response | web.StreamResponse:
        """Ingress route for request."""
        url = self._create_url(addon, path)
        source_header = _init_header(request, addon, session_data)

        # Passing the raw stream breaks requests for some webservers
        # since we just need it for POST requests really, for all other methods
        # we read the bytes and pass that to the request to the add-on
        # add-ons needs to add support with that in the configuration
        data = (
            request.content
            if request.method == "POST" and addon.ingress_stream
            else await request.read()
        )

        async with self.sys_websession.request(
            request.method,
            url,
            headers=source_header,
            params=request.query,
            allow_redirects=False,
            data=data,
            timeout=ClientTimeout(total=None),
            skip_auto_headers={hdrs.CONTENT_TYPE},
        ) as result:
            headers = _response_header(result)

            # Simple request
            if (
                hdrs.CONTENT_LENGTH in result.headers
                and int(result.headers.get(hdrs.CONTENT_LENGTH, 0)) < 4_194_000
            ):
                # Return Response
                body = await result.read()
                return web.Response(
                    headers=headers,
                    status=result.status,
                    content_type=result.content_type,
                    body=body,
                )

            # Stream response
            response = web.StreamResponse(status=result.status, headers=headers)
            response.content_type = result.content_type

            try:
                await response.prepare(request)
                async for data in result.content.iter_chunked(4096):
                    await response.write(data)

            except (
                aiohttp.ClientError,
                aiohttp.ClientPayloadError,
                ConnectionResetError,
            ) as err:
                _LOGGER.error("Stream error with %s: %s", url, err)

            return response

    async def _find_user_by_id(self, user_id: str) -> IngressSessionDataUser | None:
        """Find user object by the user's ID."""
        try:
            list_of_users = await self.sys_homeassistant.get_users()
        except (HomeAssistantAPIError, TypeError) as err:
            _LOGGER.error(
                "%s error occurred while requesting list of users: %s", type(err), err
            )
            return None

        if list_of_users is not None:
            self._list_of_users = list_of_users

        return next((user for user in self._list_of_users if user.id == user_id), None)


def _init_header(
    request: web.Request, addon: Addon, session_data: IngressSessionData | None
) -> CIMultiDict | dict[str, str]:
    """Create initial header."""
    headers = {}

    if session_data is not None:
        headers[HEADER_REMOTE_USER_ID] = session_data.user.id
        headers[HEADER_REMOTE_USER_NAME] = session_data.user.username
        headers[HEADER_REMOTE_USER_DISPLAY_NAME] = session_data.user.display_name

    # filter flags
    for name, value in request.headers.items():
        if name in (
            hdrs.CONTENT_LENGTH,
            hdrs.CONTENT_ENCODING,
            hdrs.TRANSFER_ENCODING,
            hdrs.SEC_WEBSOCKET_EXTENSIONS,
            hdrs.SEC_WEBSOCKET_PROTOCOL,
            hdrs.SEC_WEBSOCKET_VERSION,
            hdrs.SEC_WEBSOCKET_KEY,
            istr(HEADER_TOKEN),
            istr(HEADER_TOKEN_OLD),
        ):
            continue
        headers[name] = value

    # Update X-Forwarded-For
    forward_for = request.headers.get(hdrs.X_FORWARDED_FOR)
    connected_ip = ip_address(request.transport.get_extra_info("peername")[0])
    headers[hdrs.X_FORWARDED_FOR] = f"{forward_for}, {connected_ip!s}"

    return headers


def _response_header(response: aiohttp.ClientResponse) -> dict[str, str]:
    """Create response header."""
    headers = {}

    for name, value in response.headers.items():
        if name in (
            hdrs.TRANSFER_ENCODING,
            hdrs.CONTENT_LENGTH,
            hdrs.CONTENT_TYPE,
            hdrs.CONTENT_ENCODING,
        ):
            continue
        headers[name] = value

    return headers


def _is_websocket(request: web.Request) -> bool:
    """Return True if request is a websocket."""
    headers = request.headers

    if (
        "upgrade" in headers.get(hdrs.CONNECTION, "").lower()
        and headers.get(hdrs.UPGRADE, "").lower() == "websocket"
    ):
        return True
    return False


async def _websocket_forward(ws_from, ws_to):
    """Handle websocket message directly."""
    try:
        async for msg in ws_from:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await ws_to.send_str(msg.data)
            elif msg.type == aiohttp.WSMsgType.BINARY:
                await ws_to.send_bytes(msg.data)
            elif msg.type == aiohttp.WSMsgType.PING:
                await ws_to.ping()
            elif msg.type == aiohttp.WSMsgType.PONG:
                await ws_to.pong()
            elif ws_to.closed:
                await ws_to.close(code=ws_to.close_code, message=msg.extra)
    except RuntimeError:
        _LOGGER.warning("Ingress Websocket runtime error")
