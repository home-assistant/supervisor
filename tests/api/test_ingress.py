"""Test ingress API."""

import asyncio
from collections.abc import AsyncGenerator, Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
from aiohttp import WSCloseCode, WSMsgType, hdrs, web
from aiohttp.test_utils import TestClient, TestServer, make_mocked_request
from multidict import CIMultiDictProxy
import pytest

from supervisor.api.const import WEBSOCKETS
from supervisor.api.ingress import _init_header
from supervisor.apps.app import App
from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import HomeAssistantWSError

ADMIN_USER = {
    "id": "admin-id",
    "name": "Admin",
    "username": "admin",
    "is_active": True,
    "group_ids": ["system-admin"],
}
REGULAR_USER = {
    "id": "user-id",
    "name": "User",
    "username": "user",
    "is_active": True,
    "group_ids": ["system-users"],
}


@pytest.fixture(name="core_users")
def fixture_core_users(ha_ws_client: AsyncMock) -> AsyncMock:
    """Mock the Core user list with an admin and a regular user."""
    ha_ws_client.async_send_command.return_value = [ADMIN_USER, REGULAR_USER]
    return ha_ws_client


@pytest.fixture(name="real_websession")
async def fixture_real_websession(
    coresys: CoreSys,
) -> AsyncGenerator[aiohttp.ClientSession]:
    """Fixture for real aiohttp ClientSession for ingress proxy tests."""
    session = aiohttp.ClientSession()
    coresys._websession = session  # pylint: disable=W0212
    yield session
    await session.close()


@pytest.mark.usefixtures("core_users")
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
        resp = await api_client.post(
            f"{prefix}/ingress/session", json={"user_id": "admin-id"}
        )
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


async def test_validate_session_invalid(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test validating an unknown ingress session returns a JSON error."""
    api_client, prefix = api_client_with_prefix
    with patch(
        "aiohttp.web_request.BaseRequest.__getitem__",
        return_value=coresys.homeassistant,
    ):
        resp = await api_client.post(
            f"{prefix}/ingress/validate_session",
            json={"session": "non-existing"},
        )

    assert resp.status == 401
    assert await resp.json() == {
        "result": "error",
        "message": "Ingress session is not valid",
    }


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
            {"id": "some-id", "name": "Some Name", "username": "sn", "is_active": True}
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
        assert coresys.ingress.users["some-id"].is_admin is False


async def test_create_session_requires_user_id(api_client: TestClient):
    """Test session creation rejects requests without a user ID."""
    resp = await api_client.post("/ingress/session")
    assert resp.status == 400


@pytest.mark.parametrize(
    ("list_users_mock", "user_id", "expected_admin"),
    [
        pytest.param(
            {"return_value": [ADMIN_USER]}, "admin-id", True, id="admin_group"
        ),
        pytest.param(
            {"return_value": [{"id": "owner-id", "is_owner": True, "is_active": True}]},
            "owner-id",
            True,
            id="owner",
        ),
        pytest.param(
            {"return_value": [REGULAR_USER]}, "user-id", False, id="regular_user"
        ),
        pytest.param(
            {"side_effect": HomeAssistantWSError("offline")},
            "admin-id",
            None,
            id="lookup_error",
        ),
    ],
)
async def test_create_session_resolves_role(
    api_client: TestClient,
    coresys: CoreSys,
    ha_ws_client: AsyncMock,
    list_users_mock: dict[str, Any],
    user_id: str,
    expected_admin: bool | None,
):
    """Test the admin role is derived from the Core user record on creation."""
    ha_ws_client.async_send_command.configure_mock(**list_users_mock)

    resp = await api_client.post("/ingress/session", json={"user_id": user_id})
    session = (await resp.json())["data"]["session"]

    session_data = coresys.ingress.get_session_data(session)
    assert session_data is not None
    assert session_data.user.id == user_id
    user = coresys.ingress.users.get(user_id)
    assert (user.is_admin if user else None) is expected_admin


async def test_create_session_refreshes_shared_role(
    api_client: TestClient, coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test a new session updates the role shared by all sessions of a user."""
    ha_ws_client.async_send_command.return_value = [ADMIN_USER]
    await api_client.post("/ingress/session", json={"user_id": "admin-id"})
    assert coresys.ingress.users["admin-id"].is_admin is True

    ha_ws_client.async_send_command.return_value = [{**ADMIN_USER, "group_ids": []}]
    await api_client.post("/ingress/session", json={"user_id": "admin-id"})
    assert coresys.ingress.users["admin-id"].is_admin is False


@pytest.mark.parametrize(
    ("users", "user_id"),
    [
        pytest.param([REGULAR_USER], "unknown-id", id="unknown_user"),
        pytest.param([{**ADMIN_USER, "is_active": False}], "admin-id", id="inactive"),
    ],
)
async def test_create_session_rejects_invalid_user(
    api_client: TestClient,
    ha_ws_client: AsyncMock,
    users: list[dict[str, Any]],
    user_id: str,
):
    """Test session creation is rejected for unknown or deactivated users."""
    ha_ws_client.async_send_command.return_value = users

    resp = await api_client.post("/ingress/session", json={"user_id": user_id})
    assert resp.status == 400


@pytest.mark.parametrize(
    ("user_id", "panel_admin", "expected_status"),
    [
        pytest.param("user-id", True, 403, id="user_admin_panel"),
        pytest.param("user-id", False, 200, id="user_regular_panel"),
        pytest.param("admin-id", True, 200, id="admin_admin_panel"),
        pytest.param("admin-id", False, 200, id="admin_regular_panel"),
    ],
)
@pytest.mark.usefixtures("core_users")
async def test_ingress_proxy_enforces_panel_admin(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    real_websession: aiohttp.ClientSession,
    user_id: str,
    panel_admin: bool,
    expected_status: int,
):
    """Test non-admin sessions cannot access apps with an admin-only panel."""
    api_client, prefix = api_client_with_prefix

    async def mock_app_handler(request: web.Request) -> web.Response:
        return web.Response(body=b"ok", content_type="text/plain")

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", mock_app_handler)
    app_server = TestServer(app)
    await app_server.start_server()

    try:
        resp = await api_client.post(
            f"{prefix}/ingress/session", json={"user_id": user_id}
        )
        session = (await resp.json())["data"]["session"]

        mock_app = MagicMock(spec=App)
        mock_app.slug = "test_addon"
        mock_app.panel_admin = panel_admin
        mock_app.ip_address = app_server.host
        mock_app.ingress_port = app_server.port
        mock_app.ingress_stream = False

        ingress_token = coresys.ingress.create_session()
        with patch.object(coresys.ingress, "get", return_value=mock_app):
            resp = await api_client.get(
                f"{prefix}/ingress/{ingress_token}/",
                cookies={"ingress_session": session},
            )
            assert resp.status == expected_status
    finally:
        await app_server.close()


@pytest.mark.parametrize(
    (
        "list_users_mock",
        "panel_admin",
        "expected_status",
        "expected_headers",
        "session_kept",
    ),
    [
        pytest.param(
            {"return_value": [ADMIN_USER]},
            True,
            200,
            {
                "X-Remote-User-Name": "admin",
                "X-Remote-User-Display-Name": "Admin",
                "X-Remote-User-Groups": "system-admin",
            },
            True,
            id="resolved_admin",
        ),
        pytest.param(
            {"return_value": [{**ADMIN_USER, "name": "Renamed", "group_ids": []}]},
            False,
            200,
            {"X-Remote-User-Name": "admin", "X-Remote-User-Display-Name": "Renamed"},
            True,
            id="resolved_renamed_demoted_user",
        ),
        pytest.param(
            {"return_value": [{**ADMIN_USER, "is_owner": True, "group_ids": []}]},
            True,
            200,
            {
                "X-Remote-User-Name": "admin",
                "X-Remote-User-Display-Name": "Admin",
                "X-Remote-User-Groups": "system-admin",
            },
            True,
            id="resolved_owner_without_admin_group",
        ),
        pytest.param(
            {"return_value": [REGULAR_USER]}, True, 401, None, False, id="removed_user"
        ),
        pytest.param(
            {"return_value": [{**ADMIN_USER, "is_active": False}]},
            False,
            401,
            None,
            False,
            id="inactive_user",
        ),
        pytest.param(
            {"side_effect": HomeAssistantWSError("offline")},
            True,
            403,
            None,
            True,
            id="still_offline",
        ),
        pytest.param(
            {"side_effect": HomeAssistantWSError("offline")},
            False,
            200,
            {},
            True,
            id="still_offline_regular_panel",
        ),
    ],
)
async def test_ingress_proxy_resolves_unresolved_session(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    ha_ws_client: AsyncMock,
    real_websession: aiohttp.ClientSession,
    list_users_mock: dict[str, Any],
    panel_admin: bool,
    expected_status: int,
    expected_headers: dict[str, str] | None,
    session_kept: bool,
):
    """Test a session without a resolved user is resolved from Core on first use."""
    api_client, prefix = api_client_with_prefix
    received_headers: dict[str, str] | None = None

    async def mock_app_handler(request: web.Request) -> web.Response:
        nonlocal received_headers
        received_headers = {
            key: value
            for key, value in request.headers.items()
            if key
            in (
                "X-Remote-User-Name",
                "X-Remote-User-Display-Name",
                "X-Remote-User-Groups",
            )
        }
        return web.Response(body=b"ok", content_type="text/plain")

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", mock_app_handler)
    app_server = TestServer(app)
    await app_server.start_server()

    try:
        ha_ws_client.async_send_command.side_effect = HomeAssistantWSError("offline")
        resp = await api_client.post(
            f"{prefix}/ingress/session", json={"user_id": "admin-id"}
        )
        session = (await resp.json())["data"]["session"]
        assert coresys.ingress.users == {}

        ha_ws_client.async_send_command.configure_mock(
            **{"side_effect": None, **list_users_mock}
        )

        mock_app = MagicMock(spec=App)
        mock_app.slug = "test_addon"
        mock_app.panel_admin = panel_admin
        mock_app.ip_address = app_server.host
        mock_app.ingress_port = app_server.port
        mock_app.ingress_stream = False

        ingress_token = coresys.ingress.create_session()
        with patch.object(coresys.ingress, "get", return_value=mock_app):
            resp = await api_client.get(
                f"{prefix}/ingress/{ingress_token}/",
                cookies={"ingress_session": session},
            )
            assert resp.status == expected_status
        assert received_headers == expected_headers
        assert (session in coresys.ingress.sessions) is session_kept
    finally:
        await app_server.close()


async def test_ingress_proxy_uses_cached_user(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    ha_ws_client: AsyncMock,
    real_websession: aiohttp.ClientSession,
):
    """Test a session created while Core was offline gets the cached user record."""
    api_client, prefix = api_client_with_prefix
    received_headers: dict[str, str] | None = None

    async def mock_app_handler(request: web.Request) -> web.Response:
        nonlocal received_headers
        received_headers = {
            key: value
            for key, value in request.headers.items()
            if key
            in (
                "X-Remote-User-Name",
                "X-Remote-User-Display-Name",
                "X-Remote-User-Groups",
            )
        }
        return web.Response(body=b"ok", content_type="text/plain")

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", mock_app_handler)
    app_server = TestServer(app)
    await app_server.start_server()

    try:
        ha_ws_client.async_send_command.side_effect = HomeAssistantWSError("offline")
        resp = await api_client.post(
            f"{prefix}/ingress/session", json={"user_id": "admin-id"}
        )
        offline_session = (await resp.json())["data"]["session"]

        ha_ws_client.async_send_command.configure_mock(
            side_effect=None, return_value=[ADMIN_USER]
        )
        await api_client.post(f"{prefix}/ingress/session", json={"user_id": "admin-id"})
        ha_ws_client.async_send_command.reset_mock()

        mock_app = MagicMock(spec=App)
        mock_app.slug = "test_addon"
        mock_app.panel_admin = True
        mock_app.ip_address = app_server.host
        mock_app.ingress_port = app_server.port
        mock_app.ingress_stream = False

        ingress_token = coresys.ingress.create_session()
        with patch.object(coresys.ingress, "get", return_value=mock_app):
            resp = await api_client.get(
                f"{prefix}/ingress/{ingress_token}/",
                cookies={"ingress_session": offline_session},
            )
            assert resp.status == 200
        assert received_headers == {
            "X-Remote-User-Name": "admin",
            "X-Remote-User-Display-Name": "Admin",
            "X-Remote-User-Groups": "system-admin",
        }
        ha_ws_client.async_send_command.assert_not_called()
    finally:
        await app_server.close()


@pytest.mark.usefixtures("core_users")
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
        resp = await api_client.post(
            f"{prefix}/ingress/session", json={"user_id": "admin-id"}
        )
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


@pytest.mark.usefixtures("core_users")
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
        resp = await api_client.post(
            f"{prefix}/ingress/session", json={"user_id": "admin-id"}
        )
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


@pytest.mark.usefixtures("core_users")
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
        resp = await api_client.post("/ingress/session", json={"user_id": "admin-id"})
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

        shutdown_task = asyncio.create_task(api_client.server.app.shutdown())
        msg = await websocket.receive()
        await shutdown_task

        assert msg.type == WSMsgType.CLOSE
        assert msg.data == WSCloseCode.GOING_AWAY
        async with asyncio.timeout(1):
            await upstream_closed.wait()
    finally:
        await app_server.close()


@pytest.mark.usefixtures("core_users")
async def test_ingress_websocket_closed_when_stopping(
    api_client: TestClient, coresys: CoreSys
):
    """Test websocket upgrades completing after API stop began are closed."""
    resp = await api_client.post("/ingress/session", json={"user_id": "admin-id"})
    session = (await resp.json())["data"]["session"]

    mock_app = MagicMock(spec=App)
    mock_app.slug = "test_app"
    mock_app.ip_address = "127.0.0.1"
    mock_app.ingress_port = 1

    await coresys.core.set_state(CoreState.STOPPING)
    ingress_token = coresys.ingress.create_session()
    with patch.object(coresys.ingress, "get", return_value=mock_app):
        websocket = await api_client.ws_connect(
            f"/ingress/{ingress_token}/ws",
            headers={hdrs.COOKIE: f"ingress_session={session}"},
        )
    msg = await websocket.receive()

    assert msg.type == WSMsgType.CLOSE
    assert msg.data == WSCloseCode.GOING_AWAY


FORGED_HEADERS = {
    "X-Remote-User-Id": "victim-id",
    "X-Remote-User-Name": "victim",
    "X-Remote-User-Display-Name": "Victim",
    "X-Remote-User-Groups": "system-admin",
    "X-Supervisor-Token": "forged-token",
    "X-Hassio-Key": "forged-key",
}
EXPECTED_IDENTITY_HEADERS = {
    "x-remote-user-id": "user-id",
    "x-remote-user-name": "user",
    "x-remote-user-display-name": "User",
    "x-remote-user-groups": "system-users",
}

HEADER_CASES = [
    pytest.param(str, id="exact_case"),
    pytest.param(str.lower, id="lower_case"),
    pytest.param(str.upper, id="upper_case"),
    pytest.param(str.title, id="title_case"),
]


def _identity_headers(headers: CIMultiDictProxy[str]) -> dict[str, list[str]]:
    """Collect every variant of the identity and token headers an app received."""
    return {
        name.lower(): headers.getall(name)
        for name in {name.lower() for name in headers}
        if name.lower() in {key.lower() for key in FORGED_HEADERS}
    }


@pytest.mark.usefixtures("core_users")
@pytest.mark.parametrize("header_case", HEADER_CASES)
async def test_ingress_proxy_drops_forged_identity_headers(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    real_websession: aiohttp.ClientSession,
    header_case: Callable[[str], str],
):
    """Test client-supplied identity headers are dropped in any letter case."""
    api_client, prefix = api_client_with_prefix
    received_headers: dict[str, list[str]] | None = None

    async def mock_app_handler(request: web.Request) -> web.Response:
        nonlocal received_headers
        received_headers = _identity_headers(request.headers)
        return web.Response(body=b"ok", content_type="text/plain")

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", mock_app_handler)
    app_server = TestServer(app)
    await app_server.start_server()

    try:
        resp = await api_client.post(
            f"{prefix}/ingress/session", json={"user_id": "user-id"}
        )
        session = (await resp.json())["data"]["session"]

        mock_app = MagicMock(spec=App)
        mock_app.slug = "test_app"
        mock_app.panel_admin = False
        mock_app.ip_address = app_server.host
        mock_app.ingress_port = app_server.port
        mock_app.ingress_stream = False

        ingress_token = coresys.ingress.create_session()
        with patch.object(coresys.ingress, "get", return_value=mock_app):
            resp = await api_client.get(
                f"{prefix}/ingress/{ingress_token}/",
                cookies={"ingress_session": session},
                headers={
                    header_case(name): value for name, value in FORGED_HEADERS.items()
                },
            )
            assert resp.status == 200
        assert received_headers == {
            name: [value] for name, value in EXPECTED_IDENTITY_HEADERS.items()
        }
    finally:
        await app_server.close()


@pytest.mark.usefixtures("core_users")
@pytest.mark.parametrize("header_case", HEADER_CASES)
async def test_ingress_websocket_drops_forged_identity_headers(
    api_client: TestClient,
    coresys: CoreSys,
    real_websession: aiohttp.ClientSession,
    header_case: Callable[[str], str],
):
    """Test client-supplied identity headers are dropped on websocket upgrades."""
    received_headers: dict[str, list[str]] | None = None

    async def mock_app_handler(request: web.Request) -> web.WebSocketResponse:
        nonlocal received_headers
        received_headers = _identity_headers(request.headers)
        websocket = web.WebSocketResponse()
        await websocket.prepare(request)
        await websocket.close()
        return websocket

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", mock_app_handler)
    app_server = TestServer(app)
    await app_server.start_server()

    try:
        resp = await api_client.post("/ingress/session", json={"user_id": "user-id"})
        session = (await resp.json())["data"]["session"]

        mock_app = MagicMock(spec=App)
        mock_app.slug = "test_app"
        mock_app.panel_admin = False
        mock_app.ip_address = app_server.host
        mock_app.ingress_port = app_server.port

        ingress_token = coresys.ingress.create_session()
        with patch.object(coresys.ingress, "get", return_value=mock_app):
            websocket = await api_client.ws_connect(
                f"/ingress/{ingress_token}/ws",
                headers={
                    hdrs.COOKIE: f"ingress_session={session}",
                    **{
                        header_case(name): value
                        for name, value in FORGED_HEADERS.items()
                    },
                },
            )
            await websocket.receive()
            await websocket.close()
        assert received_headers == {
            name: [value] for name, value in EXPECTED_IDENTITY_HEADERS.items()
        }
    finally:
        await app_server.close()


@pytest.mark.parametrize(
    ("peername", "expected"),
    [
        pytest.param(("172.30.32.1", 54321), "192.168.1.10, 172.30.32.1", id="tcp"),
        pytest.param("", "192.168.1.10", id="unix"),
    ],
)
def test_init_header_forwarded_for(peername: tuple[str, int] | str, expected: str):
    """Test X-Forwarded-For only appends the peer when it has an address."""
    transport = MagicMock()
    transport.get_extra_info.return_value = peername
    request = make_mocked_request(
        "GET",
        "/",
        headers={hdrs.X_FORWARDED_FOR: "192.168.1.10"},
        transport=transport,
    )

    headers = _init_header(request, MagicMock(spec=App), None)

    assert headers.getall(hdrs.X_FORWARDED_FOR) == [expected]
