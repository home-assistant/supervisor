"""Check ports."""

import asyncio
from ipaddress import ip_address
import socket

from supervisor.utils import check_port

LOCALHOST = ip_address("127.0.0.1")


async def test_exists_open_port():
    """Test a port with a listening service."""
    server = await asyncio.start_server(lambda _r, w: w.close(), str(LOCALHOST), 0)
    port = server.sockets[0].getsockname()[1]

    async with server:
        assert await check_port(LOCALHOST, port)


async def test_not_exists_port():
    """Test a port without a listening service."""
    # Bound but not listening, so nothing else can take the port meanwhile
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((str(LOCALHOST), 0))
        port = sock.getsockname()[1]

        assert not await check_port(LOCALHOST, port)
