"""Test Home Assistant proxy."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Coroutine, Generator
from json import dumps
from typing import Any, cast
from unittest.mock import patch

from aiohttp import ClientWebSocketResponse
from aiohttp.http_websocket import WSMessage, WSMsgType
from aiohttp.test_utils import TestClient
import pytest

from supervisor.addons import AddonManager
from supervisor.addons.addon import Addon
from supervisor.api.proxy import APIProxy
from supervisor.coresys import CoreSys


def id_generator() -> Generator[int, None, None]:
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


WebSocketGenerator = Callable[..., Coroutine[Any, Any, MockHAClientWebSocket]]


@pytest.fixture(name="proxy_ws_client")
async def fixture_proxy_ws_client(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_ssh: Addon,
) -> WebSocketGenerator:
    """Websocket client fixture connected to websocket server."""

    async def create_client(coresys: CoreSys = coresys) -> MockHAClientWebSocket:
        """Create a websocket client."""
        websocket = await api_client.ws_connect("/core/websocket")
        auth_resp = await websocket.receive_json()
        assert auth_resp["type"] == "auth_required"
        await websocket.send_json({"type": "auth", "access_token": "dummy"})

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

    with patch.object(AddonManager, "from_token", return_value=install_addon_ssh):
        yield create_client


@pytest.fixture(name="ha_ws_server")
async def fixture_ha_ws_server() -> MockHAServerWebSocket:
    """Mock HA WS server for testing."""
    with patch.object(
        APIProxy,
        "_websocket_client",
        return_value=(mock_server := MockHAServerWebSocket()),
    ):
        yield mock_server


async def test_proxy_message(
    proxy_ws_client: WebSocketGenerator,
    ha_ws_server: MockHAServerWebSocket,
    coresys: CoreSys,
):
    """Test proxy a message to and from Home Assistant."""
    client: MockHAClientWebSocket = await proxy_ws_client(coresys)

    await client.send_json_auto_id({"hello": "world"})
    proxied_msg = await ha_ws_server.incoming.get()
    assert proxied_msg.type == WSMsgType.TEXT
    assert proxied_msg.data == '{"hello": "world", "id": 1}'

    await ha_ws_server.respond_json({"world": "received"})
    assert await client.receive_json() == {"world": "received", "id": 1}


async def test_proxy_binary_message(
    proxy_ws_client: WebSocketGenerator,
    ha_ws_server: MockHAServerWebSocket,
    coresys: CoreSys,
):
    """Test proxy a binary message to and from Home Assistant."""
    client: MockHAClientWebSocket = await proxy_ws_client(coresys)

    await client.send_bytes(b"hello world")
    proxied_msg = await ha_ws_server.incoming.get()
    assert proxied_msg.type == WSMsgType.BINARY
    assert proxied_msg.data == b"hello world"

    await ha_ws_server.respond_bytes(b"world received")
    assert await client.receive_bytes() == b"world received"
