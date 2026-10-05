"""Test ingress API."""

import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
from aiohttp import WSCloseCode, WSMsgType, hdrs, web
from aiohttp.test_utils import TestClient, TestServer
import pytest

from supervisor.api.const import WEBSOCKETS
from supervisor.apps.app import App
from supervisor.coresys import CoreSys


@pytest.fixture(name="real_websession")
async def fixture_real_websession(
    coresys: CoreSys,
) -> AsyncGenerator[aiohttp.ClientSession]:
    """Fixture for real aiohttp ClientSession for ingress proxy tests."""
    session = aiohttp.ClientSession()
    coresys._websession = session  # pylint: disable=W0212
    yield session
    await session.close()


async def test_validate_session(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test validating ingress session."""
    api_client, prefix = api_client_with_prefix
    with patch("aiohttp.web_request.BaseRequest.__getitem__", return_value=None):
        resp = await api_client.post(
            f"{prefix}/ingress/validate_session",
            json={"session": "non-existing"},
        )
        assert resp.status == 401

    with patch(
        "aiohttp.web_request.BaseRequest.__getitem__",
        return_value=coresys.homeassistant,
    ):
        resp = await api_client.post(f"{prefix}/ingress/session")
        result = await resp.json()

        assert "session" in result["data"]
        session = result["data"]["session"]
        assert session in coresys.ingress.sessions

        valid_time = coresys.ingress.sessions[session]

        resp = await api_client.post(
            f"{prefix}/ingress/validate_session",
            json={"session": session},
        )
        assert resp.status == 200
        assert await resp.json() == {"result": "ok", "data": {}}

        assert coresys.ingress.sessions[session] > valid_time


async def test_validate_session_with_user_id(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    ha_ws_client: AsyncMock,
):
    """Test validating ingress session with user ID passed."""
    api_client, prefix = api_client_with_prefix
    with patch("aiohttp.web_request.BaseRequest.__getitem__", return_value=None):
        resp = await api_client.post(
            f"{prefix}/ingress/validate_session",
            json={"session": "non-existing"},
        )
        assert resp.status == 401

    with patch(
        "aiohttp.web_request.BaseRequest.__getitem__",
        return_value=coresys.homeassistant,
    ):
        ha_ws_client.async_send_command.return_value = [
            {"id": "some-id", "name": "Some Name", "username": "sn"}
        ]

        resp = await api_client.post(
            f"{prefix}/ingress/session", json={"user_id": "some-id"}
        )
        result = await resp.json()

        assert {"type": "config/auth/list"} in [
            call.args[0] for call in ha_ws_client.async_send_command.call_args_list
        ]

        assert "session" in result["data"]
        session = result["data"]["session"]
        assert session in coresys.ingress.sessions

        valid_time = coresys.ingress.sessions[session]

        resp = await api_client.post(
            f"{prefix}/ingress/validate_session",
            json={"session": session},
        )
        assert resp.status == 200
        assert await resp.json() == {"result": "ok", "data": {}}

        assert coresys.ingress.sessions[session] > valid_time

        assert session in coresys.ingress.sessions_data
        assert coresys.ingress.get_session_data(session).user.id == "some-id"
        assert coresys.ingress.get_session_data(session).user.username == "sn"
        assert coresys.ingress.get_session_data(session).user.name == "Some Name"


async def test_ingress_proxy_no_content_type_for_empty_body_responses(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    real_websession: aiohttp.ClientSession,
):
    """Test that empty body responses don't get Content-Type header."""
    api_client, prefix = api_client_with_prefix

    # Create a mock app backend server that returns various status codes
    async def mock_app_handler(request: web.Request) -> web.Response:
        """Mock app handler that returns different status codes based on path."""
        path = request.path

        if path == "/204":
            # 204 No Content - should not have Content-Type
            return web.Response(status=204)
        if path == "/304":
            # 304 Not Modified - should not have Content-Type
            return web.Response(status=304)
        if path == "/100":
            # 100 Continue - should not have Content-Type
            return web.Response(status=100)
        if path == "/head":
            # HEAD request - should have Content-Type (same as GET would)
            return web.Response(body=b"test", content_type="text/html")
        if path == "/200":
            # 200 OK with body - should have Content-Type
            return web.Response(body=b"test content", content_type="text/plain")
        if path == "/200-no-content-type":
            # 200 OK without explicit Content-Type - should get default
            return web.Response(body=b"test content")
        if path == "/200-json":
            # 200 OK with JSON - should preserve Content-Type
            return web.Response(
                body=b'{"key": "value"}', content_type="application/json"
            )
        return web.Response(body=b"default", content_type="text/html")

    # Create test server for mock app
    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", mock_app_handler)
    app_server = TestServer(app)
    await app_server.start_server()

    try:
        # Create ingress session
        resp = await api_client.post(f"{prefix}/ingress/session")
        result = await resp.json()
        session = result["data"]["session"]

        # Create a mock app
        mock_app = MagicMock(spec=App)
        mock_app.slug = "test_addon"
        mock_app.ip_address = app_server.host
        mock_app.ingress_port = app_server.port
        mock_app.ingress_stream = False

        # Generate an ingress token and register the app
        ingress_token = coresys.ingress.create_session()
        with patch.object(coresys.ingress, "get", return_value=mock_app):
            # Test 204 No Content - should NOT have Content-Type
            resp = await api_client.get(
                f"{prefix}/ingress/{ingress_token}/204",
                cookies={"ingress_session": session},
            )
            assert resp.status == 204
            assert hdrs.CONTENT_TYPE not in resp.headers

            # Test 304 Not Modified - should NOT have Content-Type
            resp = await api_client.get(
                f"{prefix}/ingress/{ingress_token}/304",
                cookies={"ingress_session": session},
            )
            assert resp.status == 304
            assert hdrs.CONTENT_TYPE not in resp.headers

            # Test HEAD request - SHOULD have Content-Type (same as GET)
            # per RFC 9110: HEAD should return same headers as GET
            resp = await api_client.head(
                f"{prefix}/ingress/{ingress_token}/head",
                cookies={"ingress_session": session},
            )
            assert resp.status == 200
            assert hdrs.CONTENT_TYPE in resp.headers
            assert "text/html" in resp.headers[hdrs.CONTENT_TYPE]
            # Body should be empty for HEAD
            body = await resp.read()
            assert body == b""

            # Test 200 OK with body - SHOULD have Content-Type
            resp = await api_client.get(
                f"{prefix}/ingress/{ingress_token}/200",
                cookies={"ingress_session": session},
            )
            assert resp.status == 200
            assert hdrs.CONTENT_TYPE in resp.headers
            assert resp.headers[hdrs.CONTENT_TYPE] == "text/plain"
            body = await resp.read()
            assert body == b"test content"

            # Test 200 OK without explicit Content-Type - SHOULD get default
            resp = await api_client.get(
                f"{prefix}/ingress/{ingress_token}/200-no-content-type",
                cookies={"ingress_session": session},
            )
            assert resp.status == 200
            assert hdrs.CONTENT_TYPE in resp.headers
            # Should get application/octet-stream as default from aiohttp ClientResponse
            assert "application/octet-stream" in resp.headers[hdrs.CONTENT_TYPE]

            # Test 200 OK with JSON - SHOULD preserve Content-Type
            resp = await api_client.get(
                f"{prefix}/ingress/{ingress_token}/200-json",
                cookies={"ingress_session": session},
            )
            assert resp.status == 200
            assert hdrs.CONTENT_TYPE in resp.headers
            assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
            body = await resp.read()
            assert body == b'{"key": "value"}'

    finally:
        await app_server.close()


async def test_ingress_proxy_streams_response(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    real_websession: aiohttp.ClientSession,
):
    """Test responses without a content length are streamed to the client."""
    api_client, prefix = api_client_with_prefix

    async def mock_app_handler(request: web.Request) -> web.StreamResponse:
        """Stream a response in chunks without a content length."""
        response = web.StreamResponse()
        response.content_type = "text/event-stream"
        await response.prepare(request)
        for chunk in (b"data: one\n\n", b"data: two\n\n"):
            await response.write(chunk)
        await response.write_eof()
        return response

    app = web.Application()
    app.router.add_get("/stream", mock_app_handler)
    app_server = TestServer(app)
    await app_server.start_server()

    try:
        resp = await api_client.post(f"{prefix}/ingress/session")
        session = (await resp.json())["data"]["session"]

        mock_app = MagicMock(spec=App)
        mock_app.slug = "test_addon"
        mock_app.ip_address = app_server.host
        mock_app.ingress_port = app_server.port
        mock_app.ingress_stream = False

        ingress_token = coresys.ingress.create_session()
        with patch.object(coresys.ingress, "get", return_value=mock_app):
            resp = await api_client.get(
                f"{prefix}/ingress/{ingress_token}/stream",
                cookies={"ingress_session": session},
            )
            assert resp.status == 200
            assert resp.headers["X-Accel-Buffering"] == "no"
            assert resp.headers[hdrs.CONTENT_TYPE] == "text/event-stream"
            assert await resp.read() == b"data: one\n\ndata: two\n\n"

    finally:
        await app_server.close()


async def test_ingress_websocket_closed_on_api_stop(
    api_client: TestClient,
    coresys: CoreSys,
    real_websession: aiohttp.ClientSession,
):
    """Test ingress websockets are closed when the API stops."""
    upstream_closed = asyncio.Event()

    async def mock_app_handler(request: web.Request) -> web.WebSocketResponse:
        """Mock app websocket handler that stays open until closed."""
        websocket = web.WebSocketResponse()
        await websocket.prepare(request)
        async for _ in websocket:
            pass
        upstream_closed.set()
        return websocket

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", mock_app_handler)
    app_server = TestServer(app)
    await app_server.start_server()

    try:
        resp = await api_client.post("/ingress/session")
        session = (await resp.json())["data"]["session"]

        mock_app = MagicMock(spec=App)
        mock_app.slug = "test_app"
        mock_app.ip_address = app_server.host
        mock_app.ingress_port = app_server.port

        ingress_token = coresys.ingress.create_session()
        with patch.object(coresys.ingress, "get", return_value=mock_app):
            websocket = await api_client.ws_connect(
                f"/ingress/{ingress_token}/ws",
                headers={hdrs.COOKIE: f"ingress_session={session}"},
            )
        assert len(api_client.server.app[WEBSOCKETS]) == 1

        with (
            patch.object(coresys.api, "webapp", api_client.server.app),
            patch.object(coresys.api, "_site", AsyncMock()),
            patch.object(coresys.api, "_runner", AsyncMock()),
        ):
            stop_task = asyncio.create_task(coresys.api.stop())
            msg = await websocket.receive()
            await stop_task

        assert msg.type == WSMsgType.CLOSE
        assert msg.data == WSCloseCode.GOING_AWAY
        async with asyncio.timeout(1):
            await upstream_closed.wait()
    finally:
        await app_server.close()
