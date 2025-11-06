"""Test ingress API."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
from aiohttp import hdrs, web
from aiohttp.test_utils import TestClient, TestServer
import pytest

from supervisor.addons.addon import Addon
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


async def test_validate_session(api_client: TestClient, coresys: CoreSys):
    """Test validating ingress session."""
    with patch("aiohttp.web_request.BaseRequest.__getitem__", return_value=None):
        resp = await api_client.post(
            "/ingress/validate_session",
            json={"session": "non-existing"},
        )
        assert resp.status == 401

    with patch(
        "aiohttp.web_request.BaseRequest.__getitem__",
        return_value=coresys.homeassistant,
    ):
        resp = await api_client.post("/ingress/session")
        result = await resp.json()

        assert "session" in result["data"]
        session = result["data"]["session"]
        assert session in coresys.ingress.sessions

        valid_time = coresys.ingress.sessions[session]

        resp = await api_client.post(
            "/ingress/validate_session",
            json={"session": session},
        )
        assert resp.status == 200
        assert await resp.json() == {"result": "ok", "data": {}}

        assert coresys.ingress.sessions[session] > valid_time


async def test_validate_session_with_user_id(
    api_client: TestClient, coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test validating ingress session with user ID passed."""
    with patch("aiohttp.web_request.BaseRequest.__getitem__", return_value=None):
        resp = await api_client.post(
            "/ingress/validate_session",
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

        resp = await api_client.post("/ingress/session", json={"user_id": "some-id"})
        result = await resp.json()

        assert {"type": "config/auth/list"} in [
            call.args[0] for call in ha_ws_client.async_send_command.call_args_list
        ]

        assert "session" in result["data"]
        session = result["data"]["session"]
        assert session in coresys.ingress.sessions

        valid_time = coresys.ingress.sessions[session]

        resp = await api_client.post(
            "/ingress/validate_session",
            json={"session": session},
        )
        assert resp.status == 200
        assert await resp.json() == {"result": "ok", "data": {}}

        assert coresys.ingress.sessions[session] > valid_time

        assert session in coresys.ingress.sessions_data
        assert coresys.ingress.get_session_data(session).user.id == "some-id"
        assert coresys.ingress.get_session_data(session).user.username == "sn"
        assert (
            coresys.ingress.get_session_data(session).user.display_name == "Some Name"
        )


async def test_ingress_proxy_no_content_type_for_empty_body_responses(
    api_client: TestClient, coresys: CoreSys, real_websession: aiohttp.ClientSession
):
    """Test that empty body responses don't get Content-Type header."""

    # Create a mock add-on backend server that returns various status codes
    async def mock_addon_handler(request: web.Request) -> web.Response:
        """Mock add-on handler that returns different status codes based on path."""
        path = request.path

        if path == "/204":
            # 204 No Content - should not have Content-Type
            return web.Response(status=204)
        elif path == "/304":
            # 304 Not Modified - should not have Content-Type
            return web.Response(status=304)
        elif path == "/100":
            # 100 Continue - should not have Content-Type
            return web.Response(status=100)
        elif path == "/head":
            # HEAD request - should have Content-Type (same as GET would)
            return web.Response(body=b"test", content_type="text/html")
        elif path == "/200":
            # 200 OK with body - should have Content-Type
            return web.Response(body=b"test content", content_type="text/plain")
        elif path == "/200-no-content-type":
            # 200 OK without explicit Content-Type - should get default
            return web.Response(body=b"test content")
        elif path == "/200-json":
            # 200 OK with JSON - should preserve Content-Type
            return web.Response(
                body=b'{"key": "value"}', content_type="application/json"
            )
        else:
            return web.Response(body=b"default", content_type="text/html")

    # Create test server for mock add-on
    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", mock_addon_handler)
    addon_server = TestServer(app)
    await addon_server.start_server()

    try:
        # Create ingress session
        resp = await api_client.post("/ingress/session")
        result = await resp.json()
        session = result["data"]["session"]

        # Create a mock add-on
        mock_addon = MagicMock(spec=Addon)
        mock_addon.slug = "test_addon"
        mock_addon.ip_address = addon_server.host
        mock_addon.ingress_port = addon_server.port
        mock_addon.ingress_stream = False

        # Generate an ingress token and register the add-on
        ingress_token = coresys.ingress.create_session()
        with patch.object(coresys.ingress, "get", return_value=mock_addon):
            # Test 204 No Content - should NOT have Content-Type
            resp = await api_client.get(
                f"/ingress/{ingress_token}/204",
                cookies={"ingress_session": session},
            )
            assert resp.status == 204
            assert hdrs.CONTENT_TYPE not in resp.headers

            # Test 304 Not Modified - should NOT have Content-Type
            resp = await api_client.get(
                f"/ingress/{ingress_token}/304",
                cookies={"ingress_session": session},
            )
            assert resp.status == 304
            assert hdrs.CONTENT_TYPE not in resp.headers

            # Test HEAD request - SHOULD have Content-Type (same as GET)
            # per RFC 9110: HEAD should return same headers as GET
            resp = await api_client.head(
                f"/ingress/{ingress_token}/head",
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
                f"/ingress/{ingress_token}/200",
                cookies={"ingress_session": session},
            )
            assert resp.status == 200
            assert hdrs.CONTENT_TYPE in resp.headers
            assert resp.headers[hdrs.CONTENT_TYPE] == "text/plain"
            body = await resp.read()
            assert body == b"test content"

            # Test 200 OK without explicit Content-Type - SHOULD get default
            resp = await api_client.get(
                f"/ingress/{ingress_token}/200-no-content-type",
                cookies={"ingress_session": session},
            )
            assert resp.status == 200
            assert hdrs.CONTENT_TYPE in resp.headers
            # Should get application/octet-stream as default from aiohttp ClientResponse
            assert "application/octet-stream" in resp.headers[hdrs.CONTENT_TYPE]

            # Test 200 OK with JSON - SHOULD preserve Content-Type
            resp = await api_client.get(
                f"/ingress/{ingress_token}/200-json",
                cookies={"ingress_session": session},
            )
            assert resp.status == 200
            assert hdrs.CONTENT_TYPE in resp.headers
            assert "application/json" in resp.headers[hdrs.CONTENT_TYPE]
            body = await resp.read()
            assert body == b'{"key": "value"}'

    finally:
        await addon_server.close()
