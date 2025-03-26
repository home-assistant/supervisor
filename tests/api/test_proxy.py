"""Test Home Assistant proxy."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Coroutine, Generator
from json import dumps
import logging
from typing import Any, cast
from unittest.mock import patch

from aiohttp import ClientWebSocketResponse
from aiohttp.http_websocket import WSMessage, WSMsgType
from aiohttp.test_utils import TestClient
import pytest

from supervisor.addons.addon import Addon
from supervisor.api.proxy import APIProxy
from supervisor.const import ATTR_ACCESS_TOKEN


def id_generator() -> Generator[int]:
    """Generate IDs for WS messages."""
    i = 0
    while True:
        yield (i := i + 1)


class MockHAClientWebSocket(ClientWebSocketResponse):
    """Protocol for a wrapped ClientWebSocketResponse."""

    client: TestClient
    send_json_auto_id: Callable[[dict[str, Any]], Coroutine[Any, Any, None]]


class MockHAServerWebSocket:
    """Mock of HA Websocket server."""

    closed: bool = False

    def __init__(self) -> None:
        """Initialize object."""
        self.outgoing: asyncio.Queue[WSMessage] = asyncio.Queue()
        self.incoming: asyncio.Queue[WSMessage] = asyncio.Queue()
        self._id_generator = id_generator()

    def receive(self) -> Awaitable[WSMessage]:
        """Receive next message."""
        return self.outgoing.get()

    def send_str(self, data: str) -> Awaitable[None]:
        """Incoming string message."""
        return self.incoming.put(WSMessage(WSMsgType.TEXT, data, None))

    def send_bytes(self, data: bytes) -> Awaitable[None]:
        """Incoming string message."""
        return self.incoming.put(WSMessage(WSMsgType.BINARY, data, None))

    def respond_json(self, data: dict[str, Any]) -> Awaitable[None]:
        """Respond with JSON."""
        return self.outgoing.put(
            WSMessage(
                WSMsgType.TEXT, dumps(data | {"id": next(self._id_generator)}), None
            )
        )

    def respond_bytes(self, data: bytes) -> Awaitable[None]:
        """Respond with binary."""
        return self.outgoing.put(WSMessage(WSMsgType.BINARY, data, None))

    async def close(self) -> None:
        """Close connection."""
        self.closed = True


WebSocketGenerator = Callable[..., Coroutine[Any, Any, MockHAClientWebSocket]]


@pytest.fixture(name="ha_ws_server")
async def fixture_ha_ws_server() -> MockHAServerWebSocket:
    """Mock HA WS server for testing."""
    with patch.object(
        APIProxy,
        "_websocket_client",
        return_value=(mock_server := MockHAServerWebSocket()),
    ):
        yield mock_server


@pytest.fixture(name="proxy_ws_client")
def fixture_proxy_ws_client(
    api_client: TestClient, ha_ws_server: MockHAServerWebSocket
) -> WebSocketGenerator:
    """Websocket client fixture connected to websocket server."""

    async def create_client(auth_token: str) -> MockHAClientWebSocket:
        """Create a websocket client."""
        websocket = await api_client.ws_connect("/core/websocket")
        auth_resp = await websocket.receive_json()
        assert auth_resp["type"] == "auth_required"
        await websocket.send_json({"type": "auth", "access_token": auth_token})

        auth_ok = await websocket.receive_json()
        assert auth_ok["type"] == "auth_ok"

        _id_generator = id_generator()

        def _send_json_auto_id(data: dict[str, Any]) -> Coroutine[Any, Any, None]:
            data["id"] = next(_id_generator)
            return websocket.send_json(data)

        # wrap in client
        wrapped_websocket = cast(MockHAClientWebSocket, websocket)
        wrapped_websocket.client = api_client
        wrapped_websocket.send_json_auto_id = _send_json_auto_id
        return wrapped_websocket

    return create_client


async def test_proxy_message(
    proxy_ws_client: WebSocketGenerator,
    ha_ws_server: MockHAServerWebSocket,
    install_addon_ssh: Addon,
):
    """Test proxy a message to and from Home Assistant."""
    install_addon_ssh.persist[ATTR_ACCESS_TOKEN] = "abc123"
    client: MockHAClientWebSocket = await proxy_ws_client(
        install_addon_ssh.supervisor_token
    )

    await client.send_json_auto_id({"hello": "world"})
    proxied_msg = await ha_ws_server.incoming.get()
    assert proxied_msg.type == WSMsgType.TEXT
    assert proxied_msg.data == '{"hello": "world", "id": 1}'

    await ha_ws_server.respond_json({"world": "received"})
    assert await client.receive_json() == {"world": "received", "id": 1}

    assert await client.close()


async def test_proxy_binary_message(
    proxy_ws_client: WebSocketGenerator,
    ha_ws_server: MockHAServerWebSocket,
    install_addon_ssh: Addon,
):
    """Test proxy a binary message to and from Home Assistant."""
    install_addon_ssh.persist[ATTR_ACCESS_TOKEN] = "abc123"
    client: MockHAClientWebSocket = await proxy_ws_client(
        install_addon_ssh.supervisor_token
    )

    await client.send_bytes(b"hello world")
    proxied_msg = await ha_ws_server.incoming.get()
    assert proxied_msg.type == WSMsgType.BINARY
    assert proxied_msg.data == b"hello world"

    await ha_ws_server.respond_bytes(b"world received")
    assert await client.receive_bytes() == b"world received"

    assert await client.close()


@pytest.mark.parametrize("auth_token", ["abc123", "bad"])
async def test_proxy_invalid_auth(
    api_client: TestClient, install_addon_example: Addon, auth_token: str
):
    """Test invalid access token or addon with no access."""
    install_addon_example.persist[ATTR_ACCESS_TOKEN] = "abc123"
    websocket = await api_client.ws_connect("/core/websocket")
    auth_resp = await websocket.receive_json()
    assert auth_resp["type"] == "auth_required"
    await websocket.send_json({"type": "auth", "access_token": auth_token})

    auth_not_ok = await websocket.receive_json()
    assert auth_not_ok["type"] == "auth_invalid"
    assert auth_not_ok["message"] == "Invalid access"


async def test_proxy_auth_abort_log(
    api_client: TestClient,
    install_addon_example: Addon,
    caplog: pytest.LogCaptureFixture,
):
    """Test WebSocket closed during authentication gets logged."""
    install_addon_example.persist[ATTR_ACCESS_TOKEN] = "abc123"
    websocket = await api_client.ws_connect("/core/websocket")
    auth_resp = await websocket.receive_json()
    assert auth_resp["type"] == "auth_required"
    caplog.clear()
    with caplog.at_level(logging.ERROR):
        await websocket.close()
        assert (
            "Unexpected message during authentication for WebSocket API" in caplog.text
        )
