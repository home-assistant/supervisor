"""Test Unix sockets the API listens on."""

import asyncio
from collections.abc import AsyncGenerator, Callable
import errno
from pathlib import Path
import socket
from unittest.mock import patch

from aiohttp import ClientSession, UnixConnector, web
from aiohttp.test_utils import TestClient
import pytest

from supervisor.api import RestAPI
from supervisor.api.sockets import SocketRegistry
from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import (
    APISocketAlreadyRegisteredError,
    APISocketListenError,
    APISocketPrepareError,
)

REGISTRY = web.AppKey("registry", SocketRegistry)


async def _principal_handler(request: web.Request) -> web.Response:
    """Return whether the request was identified by its socket."""
    registry = request.app[REGISTRY]
    return web.Response(text=str(registry.principal_for(request) is not None))


@pytest.fixture(name="registry")
async def fixture_registry(
    coresys: CoreSys,
) -> AsyncGenerator[tuple[SocketRegistry, web.AppRunner]]:
    """Return a socket registry serving a minimal app."""
    app = web.Application()
    app.router.add_get("/", _principal_handler)
    runner = web.AppRunner(app)
    registry = SocketRegistry(coresys, runner)
    app[REGISTRY] = registry
    await runner.setup()
    yield registry, runner
    await registry.stop_all()
    await runner.cleanup()


async def _get(path: Path) -> str:
    """Request the root path over a Unix socket and return the body."""
    async with (
        ClientSession(connector=UnixConnector(path=str(path))) as session,
        session.get("http://localhost/") as resp,
    ):
        assert resp.status == 200
        return await resp.text()


def _plant_nothing(path: Path) -> None:
    """Leave the socket folder missing."""


def _plant_regular_file(path: Path) -> None:
    """Leave a regular file at the socket path."""
    path.parent.mkdir()
    path.write_text("stale")


def _plant_socket_file(path: Path) -> None:
    """Leave a socket file without listener at the socket path."""
    path.parent.mkdir()
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(str(path))
    sock.close()


@pytest.mark.parametrize(
    "plant",
    [
        pytest.param(_plant_nothing, id="missing-dir"),
        pytest.param(_plant_regular_file, id="stale-regular-file"),
        pytest.param(_plant_socket_file, id="stale-socket-file"),
    ],
)
async def test_register(
    coresys: CoreSys,
    registry: tuple[SocketRegistry, web.AppRunner],
    tmp_run_dir: Path,
    plant: Callable[[Path], None],
):
    """Test requests on a registered socket are identified by it."""
    sockets, _ = registry
    path = tmp_run_dir / "core" / "test.sock"
    await asyncio.get_running_loop().run_in_executor(None, plant, path)

    await sockets.register(coresys.homeassistant, path)

    assert sockets.paths == [str(path)]
    assert await _get(path) == "True"
    stat = await asyncio.get_running_loop().run_in_executor(None, path.stat)
    assert stat.st_mode & 0o777 == 0o600


async def test_unregister(
    coresys: CoreSys, registry: tuple[SocketRegistry, web.AppRunner], tmp_run_dir: Path
):
    """Test unregistering stops listening and removes the socket file."""
    sockets, _ = registry
    path = tmp_run_dir / "test.sock"
    await sockets.register(coresys.homeassistant, path)

    await sockets.unregister(path)

    assert not sockets.paths
    assert not await asyncio.get_running_loop().run_in_executor(None, path.exists)


async def test_stop_all(
    coresys: CoreSys, registry: tuple[SocketRegistry, web.AppRunner], tmp_run_dir: Path
):
    """Test stopping all sockets releases each of them."""
    sockets, runner = registry
    paths = [tmp_run_dir / "core.sock", tmp_run_dir / "host.sock"]
    await sockets.register(coresys.homeassistant, paths[0])
    await sockets.register(coresys.host, paths[1])

    await sockets.stop_all()

    assert not sockets.paths
    assert not runner.sites
    loop = asyncio.get_running_loop()
    assert not any([await loop.run_in_executor(None, p.exists) for p in paths])


async def test_register_twice(
    coresys: CoreSys, registry: tuple[SocketRegistry, web.AppRunner], tmp_run_dir: Path
):
    """Test a path can only be registered once."""
    sockets, _ = registry
    path = tmp_run_dir / "test.sock"
    await sockets.register(coresys.homeassistant, path)

    with pytest.raises(APISocketAlreadyRegisteredError):
        await sockets.register(coresys.host, path)


async def test_register_concurrently(
    coresys: CoreSys, registry: tuple[SocketRegistry, web.AppRunner], tmp_run_dir: Path
):
    """Test concurrent registrations of one path bind it once."""
    sockets, runner = registry
    path = tmp_run_dir / "test.sock"

    results = await asyncio.gather(
        sockets.register(coresys.homeassistant, path),
        sockets.register(coresys.host, path),
        return_exceptions=True,
    )

    assert results[0] is None
    assert isinstance(results[1], APISocketAlreadyRegisteredError)
    assert len(runner.sites) == 1
    assert await _get(path) == "True"


async def test_failed_start_does_not_poison_retry(
    coresys: CoreSys, registry: tuple[SocketRegistry, web.AppRunner], tmp_run_dir: Path
):
    """Test a failed bind leaves nothing behind that breaks a retry."""
    sockets, runner = registry
    path = tmp_run_dir / "test.sock"

    with (
        patch.object(
            asyncio.get_running_loop(), "create_unix_server", side_effect=OSError
        ),
        pytest.raises(APISocketListenError),
    ):
        await sockets.register(coresys.homeassistant, path)
    assert not runner.sites
    assert not sockets.paths

    await sockets.register(coresys.homeassistant, path)

    assert len(runner.sites) == 1
    assert await _get(path) == "True"


async def test_register_prepare_failure_logs_cause(
    coresys: CoreSys,
    registry: tuple[SocketRegistry, web.AppRunner],
    tmp_run_dir: Path,
    caplog: pytest.LogCaptureFixture,
):
    """Test the OS error behind a failed socket path preparation is logged."""
    sockets, _ = registry
    path = tmp_run_dir / "test.sock"
    await asyncio.get_running_loop().run_in_executor(None, path.mkdir)

    with pytest.raises(APISocketPrepareError):
        await sockets.register(coresys.homeassistant, path)

    assert f"Can't prepare path for API socket {path}: [Errno" in caplog.text


async def test_register_listen_failure_logs_cause(
    coresys: CoreSys,
    registry: tuple[SocketRegistry, web.AppRunner],
    tmp_run_dir: Path,
    caplog: pytest.LogCaptureFixture,
):
    """Test the OS error behind a failed socket bind is logged."""
    sockets, _ = registry
    path = tmp_run_dir / "test.sock"

    with (
        patch.object(
            asyncio.get_running_loop(),
            "create_unix_server",
            side_effect=OSError(errno.EADDRINUSE, "Address in use"),
        ),
        pytest.raises(APISocketListenError),
    ):
        await sockets.register(coresys.homeassistant, path)

    assert (
        f"Can't listen on API socket {path}: [Errno {errno.EADDRINUSE}] Address in use"
        in caplog.text
    )


async def test_principal_for_tcp(
    aiohttp_client: Callable[..., TestClient],
    registry: tuple[SocketRegistry, web.AppRunner],
):
    """Test a request on TCP has no socket principal."""
    sockets, _ = registry
    app = web.Application()
    app[REGISTRY] = sockets
    app.router.add_get("/", _principal_handler)
    client = await aiohttp_client(app)

    resp = await client.get("/")

    assert await resp.text() == "False"


async def test_api_listens_for_core(coresys: CoreSys, tmp_run_dir: Path):
    """Test the API serves Core on its socket without a token."""
    await coresys.core.set_state(CoreState.RUNNING)
    path = tmp_run_dir / "supervisor" / "core" / "supervisor.sock"
    api = RestAPI(coresys)
    with patch("supervisor.docker.supervisor.os") as os:
        os.environ = {"SUPERVISOR_NAME": "hassio_supervisor"}
        await api.load()
    await api.start()

    try:
        assert api.sockets.paths == [str(path)]
        async with (
            ClientSession(connector=UnixConnector(path=str(path))) as session,
            session.get("http://localhost/supervisor/info") as resp,
        ):
            assert resp.status == 200
    finally:
        await api.stop()

    assert not api.sockets.paths
    assert not await asyncio.get_running_loop().run_in_executor(None, path.exists)


async def test_api_retries_core_socket(coresys: CoreSys, tmp_run_dir: Path):
    """Test the API keeps retrying Core's socket until it can listen on it."""
    path = tmp_run_dir / "supervisor" / "core" / "supervisor.sock"
    loop = asyncio.get_running_loop()
    # A directory in the way makes preparing the socket path fail
    await loop.run_in_executor(None, lambda: path.mkdir(parents=True))
    api = RestAPI(coresys)

    with patch("supervisor.api.CORE_SOCKET_RETRY_MIN", 0):
        await api.start()
        try:
            assert not api.sockets.paths
            await loop.run_in_executor(None, path.rmdir)
            # pylint: disable-next=protected-access
            await asyncio.wait_for(api._core_socket_retry, timeout=5)

            assert api.sockets.paths == [str(path)]
        finally:
            await api.stop()


async def test_api_stop_cancels_core_socket_retry(coresys: CoreSys, tmp_run_dir: Path):
    """Test stopping the API ends retrying Core's socket."""
    path = tmp_run_dir / "supervisor" / "core" / "supervisor.sock"
    await asyncio.get_running_loop().run_in_executor(
        None, lambda: path.mkdir(parents=True)
    )
    api = RestAPI(coresys)
    await api.start()

    await api.stop()

    # pylint: disable-next=protected-access
    assert api._core_socket_retry.cancelled()
    assert not api.sockets.paths
