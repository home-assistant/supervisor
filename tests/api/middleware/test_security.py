"""Test API security layer."""

import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable
from http import HTTPStatus
from pathlib import Path
import time
from unittest.mock import AsyncMock, MagicMock, patch

from aiohttp import ClientSession, UnixConnector, web
from aiohttp.test_utils import TestClient, make_mocked_request
import pytest
import urllib3

from supervisor.api import RestAPI
from supervisor.api.middleware.security import FILTERS
from supervisor.apps.app import App
from supervisor.const import REQUEST_FROM, ROLE_ALL, CoreState
from supervisor.coresys import CoreSys, CoreSysAttributes
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue

# pylint: disable=redefined-outer-name


async def mock_handler(request):
    """Return OK."""
    return web.Response(text="OK")


@pytest.fixture
async def api_system(aiohttp_client, coresys: CoreSys) -> TestClient:
    """Fixture for RestAPI client."""
    api = RestAPI(coresys)
    api.webapp = web.Application()
    with patch("supervisor.docker.supervisor.os") as os:
        os.environ = {"SUPERVISOR_NAME": "hassio_supervisor"}
        await api.load()

    api.webapp.middlewares.append(api.security.block_bad_requests)
    api.webapp.middlewares.append(api.security.system_validation)
    api.webapp.router.add_get("/{all:.*}", mock_handler)

    return await aiohttp_client(api.webapp)


@pytest.fixture
async def api_token_validation(
    aiohttp_client, coresys: CoreSys, tmp_run_dir: Path
) -> AsyncGenerator[TestClient]:
    """Fixture for RestAPI client with token validation middleware."""
    api = RestAPI(coresys)
    api.webapp = web.Application()
    with patch("supervisor.docker.supervisor.os") as os:
        os.environ = {"SUPERVISOR_NAME": "hassio_supervisor"}
        await api.start()

    api.webapp.middlewares.append(api.security.token_validation)
    api.webapp.router.add_get("/{all:.*}", mock_handler)
    api.webapp.router.add_post("/{all:.*}", mock_handler)
    api.webapp.router.add_delete("/{all:.*}", mock_handler)

    yield await aiohttp_client(api.webapp)
    await api.stop()


@pytest.fixture(
    name="api_token_validation_with_prefix",
    params=[pytest.param("", id="v1"), pytest.param("/v2", id="v2")],
)
async def fixture_api_token_validation_with_prefix(
    request: pytest.FixtureRequest,
    api_token_validation: TestClient,
) -> tuple[TestClient, str]:
    """Provide (client, path_prefix) for token_validation on both API versions.

    Mirrors api_client_with_prefix, but keeps the real token_validation
    middleware (which api_client/api_client_v2 replace with a stub) so security
    checks like the blacklist are actually exercised on the v1 and v2 paths.
    """
    return api_token_validation, request.param


@pytest.fixture(name="plugin_tokens")
async def fixture_plugin_tokens(coresys: CoreSys) -> None:
    """Mock plugin tokens used in middleware."""
    # pylint: disable=protected-access
    coresys.plugins.cli._data["access_token"] = "c_123456"
    coresys.plugins.observer._data["access_token"] = "o_123456"
    # pylint: enable=protected-access


async def test_api_security_system_initialize(api_system: TestClient, coresys: CoreSys):
    """Test security."""
    await coresys.core.set_state(CoreState.INITIALIZE)

    resp = await api_system.get("/supervisor/ping")
    result = await resp.json()
    assert resp.status == 400
    assert result["result"] == "error"


async def test_api_security_system_setup(api_system: TestClient, coresys: CoreSys):
    """Test security."""
    await coresys.core.set_state(CoreState.SETUP)

    resp = await api_system.get("/supervisor/ping")
    result = await resp.json()
    assert resp.status == 400
    assert result["result"] == "error"


async def test_api_security_system_running(api_system: TestClient, coresys: CoreSys):
    """Test security."""
    await coresys.core.set_state(CoreState.RUNNING)

    resp = await api_system.get("/supervisor/ping")
    assert resp.status == 200


async def test_api_security_system_startup(api_system: TestClient, coresys: CoreSys):
    """Test security."""
    await coresys.core.set_state(CoreState.STARTUP)

    resp = await api_system.get("/supervisor/ping")
    assert resp.status == 200


@pytest.mark.parametrize(
    ("request_path", "request_params", "fail_on_query_string"),
    [
        ("/proc/self/environ", {}, False),
        ("/", {"test": "/test/../../api"}, True),
        ("/", {"test": "test/../../api"}, True),
        ("/", {"test": "/test/%2E%2E%2f%2E%2E%2fapi"}, True),
        ("/", {"test": "test/%2E%2E%2f%2E%2E%2fapi"}, True),
        ("/", {"test": "test/%252E%252E/api"}, True),
        ("/", {"test": "test/%252E%252E%2fapi"}, True),
        (
            "/",
            {"test": "test/%2525252E%2525252E%2525252f%2525252E%2525252E%2525252fapi"},
            True,
        ),
        ("/test/.%252E/api", {}, False),
        ("/test/%252E%252E/api", {}, False),
        ("/test/%2E%2E%2f%2E%2E%2fapi", {}, False),
        ("/test/%2525252E%2525252E%2525252f%2525252E%2525252E/api", {}, False),
        ("/", {"sql": ";UNION SELECT (a, b"}, True),
        ("/", {"sql": "UNION%20SELECT%20%28a%2C%20b"}, True),
        ("/UNION%20SELECT%20%28a%2C%20b", {}, False),
        ("/", {"sql": "concat(..."}, True),
        ("/", {"xss": "<script >"}, True),
        ("/<script >", {"xss": ""}, False),
        ("/%3Cscript%3E", {}, False),
    ],
)
async def test_bad_requests(
    request_path: str,
    request_params: dict[str, str],
    fail_on_query_string: bool,
    api_system: TestClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test request paths that should be filtered."""

    # Manual params handling
    if request_params:
        raw_params = "&".join(f"{val}={key}" for val, key in request_params.items())
        man_params = f"?{raw_params}"
    else:
        man_params = ""

    http = urllib3.PoolManager()
    resp = await asyncio.get_running_loop().run_in_executor(
        None,
        http.request,
        "GET",
        f"http://{api_system.host}:{api_system.port}{request_path}{man_params}",
        request_params,
    )

    assert resp.status == HTTPStatus.BAD_REQUEST

    message = "Filtered a potential harmful request to:"
    if fail_on_query_string:
        message = "Filtered a request with a potential harmful query string:"
    assert message in caplog.text


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param("<script" * 3500, id="xss"),
        pytest.param("%3Cscript" * 2700, id="xss-encoded"),
        pytest.param("union" * 4900, id="union-select"),
        pytest.param("unionall" * 3000, id="union-all-select"),
        pytest.param("concat" * 4000, id="concat"),
    ],
)
def test_filters_no_catastrophic_backtracking(payload: str) -> None:
    """Test near-miss payloads at max request line size are matched quickly."""
    start = time.perf_counter()
    assert FILTERS.search(payload) is None
    assert time.perf_counter() - start < 1


@pytest.mark.parametrize(
    ("value", "blocked"),
    [
        pytest.param("a <b> script", False, id="no-close-after-script"),
        pytest.param("<\nscript>", False, id="xss-across-lines"),
        pytest.param("x\n<SCRIPT src=y>", True, id="xss-second-line"),
        pytest.param("select union (", False, id="select-before-union"),
        pytest.param("union all select", True, id="union-all-select"),
        pytest.param("union\nselect (", False, id="union-across-lines"),
        pytest.param("concat ( ", True, id="concat"),
    ],
)
def test_filters_keyword_order(value: str, blocked: bool) -> None:
    """Test multi-keyword filters require keyword order within a line."""
    assert bool(FILTERS.search(value)) is blocked


def _versioned_path(prefix: str, path: str) -> str:
    """Translate a v1 middleware path to the requested API version.

    The v2 sub-app keeps the same paths behind a /v2 prefix, except the add-on
    routes which are renamed /addons/... -> /apps/.... The role/bypass/core_only
    expectations are otherwise identical, which is exactly the v1<->v2 pattern
    parity these tests guard.
    """
    if not prefix:
        return path
    return prefix + path.replace("/addons", "/apps")


ROLE_PATHS = [
    ("post", "/auth/reset", {"admin"}),
    ("get", "/auth/list", {"admin"}),
    ("delete", "/auth/cache", {"admin", "manager"}),
    ("get", "/auth", set(ROLE_ALL)),
    ("post", "/auth", set(ROLE_ALL)),
    ("get", "/backups/info", set(ROLE_ALL)),
    ("get", "/backups/abc123/download", {"admin", "manager", "backup"}),
    ("post", "/backups/new/full", {"admin", "manager", "backup"}),
    ("post", "/backups/abc123/restore/full", {"admin", "manager", "backup"}),
    ("get", "/core/info", set(ROLE_ALL)),
    ("post", "/core/update", {"admin", "manager", "homeassistant"}),
    ("post", "/core/restart", {"admin", "manager", "homeassistant"}),
    ("get", "/addons/self/options/config", set(ROLE_ALL)),
    ("post", "/addons/self/options", set(ROLE_ALL)),
    ("post", "/addons/self/restart", set(ROLE_ALL)),
    ("post", "/addons/self/security", {"admin"}),
    ("get", "/addons/abc123/options/config", {"admin", "manager"}),
    ("post", "/addons/abc123/options", {"admin", "manager"}),
    ("post", "/addons/abc123/restart", {"admin", "manager"}),
    ("post", "/addons/abc123/security", {"admin"}),
    ("post", "/os/datadisk/wipe", {"admin"}),
    ("get", "/os/ssh/authorized_keys", set()),
    ("post", "/os/ssh/authorized_keys", set()),
    ("delete", "/os/ssh/authorized_keys", set()),
    ("get", "/time/info", set(ROLE_ALL)),
    ("post", "/time/options", {"admin", "manager"}),
    ("post", "/addons/self/sys_options", set()),
    ("post", "/addons/abc123/sys_options", set()),
]


@pytest.mark.parametrize(
    ("request_method", "request_path", "success_roles"), ROLE_PATHS
)
@pytest.mark.usefixtures("plugin_tokens")
async def test_token_validation(
    api_token_validation_with_prefix: tuple[TestClient, str],
    install_app_example: App,
    request_method: str,
    request_path: str,
    success_roles: set[str],
):
    """Test token validation paths on both API versions."""
    client, prefix = api_token_validation_with_prefix
    request_path = _versioned_path(prefix, request_path)
    install_app_example.persist["access_token"] = "abc123"
    install_app_example.data["hassio_api"] = True
    for role in success_roles:
        install_app_example.data["hassio_role"] = role
        resp = await getattr(client, request_method)(
            request_path, headers={"Authorization": "Bearer abc123"}
        )
        assert resp.status == 200

    for role in set(ROLE_ALL) - success_roles:
        install_app_example.data["hassio_role"] = role
        resp = await getattr(client, request_method)(
            request_path, headers={"Authorization": "Bearer abc123"}
        )
        assert resp.status == 403


@pytest.mark.usefixtures("plugin_tokens")
async def test_home_assistant_paths(
    api_token_validation_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test Home Assistant only paths on both API versions."""
    client, prefix = api_token_validation_with_prefix
    coresys.homeassistant.supervisor_token = "abc123"
    resp = await client.post(
        _versioned_path(prefix, "/addons/local_test/sys_options"),
        headers={"Authorization": "Bearer abc123"},
    )
    assert resp.status == 200

    for method in ("get", "post", "delete"):
        resp = await getattr(client, method)(
            _versioned_path(prefix, "/os/ssh/authorized_keys"),
            headers={"Authorization": "Bearer abc123"},
        )
        assert resp.status == 200


@pytest.mark.usefixtures("plugin_tokens")
async def test_blacklist(
    api_token_validation_with_prefix: tuple[TestClient, str],
    install_app_example: App,
):
    """Test the Core API hassio loopback is blocked on every API version."""
    client, prefix = api_token_validation_with_prefix
    install_app_example.persist["access_token"] = "abc123"
    install_app_example.data["hassio_api"] = True
    install_app_example.data["hassio_role"] = "admin"

    # The hassio loopback is blacklisted regardless of role
    resp = await client.get(
        f"{prefix}/core/api/hassio/app", headers={"Authorization": "Bearer abc123"}
    )
    assert resp.status == 403

    # The Core auth endpoints run as the Supervisor user; an add-on must not
    # reach them through the proxy (they would allow resetting any password)
    resp = await client.get(
        f"{prefix}/core/api/hassio_auth", headers={"Authorization": "Bearer abc123"}
    )
    assert resp.status == 403
    resp = await client.post(
        f"{prefix}/core/api/hassio_auth/password_reset",
        headers={"Authorization": "Bearer abc123"},
    )
    assert resp.status == 403

    # Percent-encoded variants are matched on the fully decoded path. Only the
    # first decode happens in aiohttp; a second one would happen downstream.
    for encoded in (
        "hassio%5Fauth/password_reset",
        "hassio%255Fauth/password_reset",
        "hassio%252Fapp",
    ):
        resp = await client.post(
            f"{prefix}/core/api/{encoded}",
            headers={"Authorization": "Bearer abc123"},
        )
        assert resp.status == 403, encoded

    # A normal (non-hassio) Core API call through the same proxy is allowed
    resp = await client.get(
        f"{prefix}/core/api/states", headers={"Authorization": "Bearer abc123"}
    )
    assert resp.status == 200


@pytest.mark.usefixtures("plugin_tokens")
async def test_blacklist_legacy_alias(
    api_token_validation: TestClient,
    install_app_example: App,
):
    """Test the legacy /homeassistant proxy alias (v1 only) is blacklisted."""
    install_app_example.persist["access_token"] = "abc123"
    install_app_example.data["hassio_api"] = True
    install_app_example.data["hassio_role"] = "admin"

    resp = await api_token_validation.get(
        "/homeassistant/api/hassio/app", headers={"Authorization": "Bearer abc123"}
    )
    assert resp.status == 403


async def test_api_security_system_stopping(api_system: TestClient, coresys: CoreSys):
    """Test API requests are rejected while the Supervisor is stopping."""
    await coresys.core.set_state(CoreState.STOPPING)

    resp = await api_system.get("/supervisor/ping")
    result = await resp.json()
    assert resp.status == 400
    assert result["result"] == "error"


RECORDED: web.AppKey[list[CoreSysAttributes | None]] = web.AppKey("recorded")

type CallAPI = Callable[..., Awaitable[tuple[int, CoreSysAttributes | None]]]


async def _recording_handler(request: web.Request) -> web.Response:
    """Record who the middleware identified the request as."""
    request.app[RECORDED].append(request[REQUEST_FROM])
    return web.Response(text="OK")


@pytest.fixture(name="principals")
def fixture_principals(
    coresys: CoreSys, install_app_example: App
) -> dict[str, CoreSysAttributes]:
    """Return one principal of each kind, each with a token."""
    coresys.homeassistant.supervisor_token = "h_123456"
    # pylint: disable=protected-access
    coresys.plugins.cli._data["access_token"] = "c_123456"
    coresys.plugins.observer._data["access_token"] = "o_123456"
    # pylint: enable=protected-access
    install_app_example.persist["access_token"] = "a_123456"
    install_app_example.data["hassio_api"] = True
    return {
        "core": coresys.homeassistant,
        "host": coresys.host,
        "observer": coresys.plugins.observer,
        "app": install_app_example,
    }


TOKENS = {
    "core": "h_123456",
    "host": "c_123456",
    "observer": "o_123456",
    "app": "a_123456",
}


@pytest.fixture(name="call_api")
async def fixture_call_api(
    coresys: CoreSys,
    tmp_run_dir: Path,
    principals: dict[str, CoreSysAttributes],
) -> AsyncGenerator[CallAPI]:
    """Call the token validation middleware over TCP with a token or over a socket.

    Returns the status and who the middleware identified the caller as.
    """
    api = RestAPI(coresys)
    app = web.Application(middlewares=[api.security.token_validation])
    app[RECORDED] = []
    app.router.add_route("*", "/{all:.*}", _recording_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "127.0.0.1", 0).start()
    host, port = runner.addresses[0]

    async def call_with_token(
        kind: str, method: str, path: str, headers: dict[str, str] | None
    ) -> int:
        async with (
            ClientSession() as session,
            session.request(
                method,
                f"http://{host}:{port}{path}",
                headers=headers or {"Authorization": f"Bearer {TOKENS[kind]}"},
            ) as resp,
        ):
            return resp.status

    async def call_on_socket(
        kind: str, method: str, path: str, headers: dict[str, str] | None
    ) -> int:
        socket_path = tmp_run_dir / f"{kind}.sock"
        await api.sockets.register(principals[kind], socket_path, runner=runner)
        try:
            async with (
                ClientSession(
                    connector=UnixConnector(path=str(socket_path))
                ) as session,
                session.request(
                    method, f"http://localhost{path}", headers=headers
                ) as resp,
            ):
                return resp.status
        finally:
            await api.sockets.unregister(socket_path)

    transports = {"token": call_with_token, "socket": call_on_socket}

    async def call(
        transport: str,
        kind: str,
        method: str,
        path: str,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, CoreSysAttributes | None]:
        app[RECORDED].clear()
        status = await transports[transport](kind, method, path, headers)
        return status, next(iter(app[RECORDED]), None)

    yield call
    await api.sockets.stop_all()
    await runner.cleanup()


@pytest.mark.parametrize("transport", ["token", "socket"])
@pytest.mark.parametrize(
    ("kind", "method", "path", "status", "request_from"),
    [
        pytest.param("core", "get", "/supervisor/info", 200, "core", id="core-info"),
        pytest.param(
            "core",
            "post",
            "/addons/local_test/sys_options",
            200,
            "core",
            id="core-core-only",
        ),
        pytest.param(
            "core", "post", "/os/ssh/authorized_keys", 200, "core", id="core-ssh"
        ),
        pytest.param(
            "host", "post", "/supervisor/options", 200, "host", id="host-options"
        ),
        pytest.param(
            "host",
            "post",
            "/addons/local_test/sys_options",
            403,
            None,
            id="host-core-only",
        ),
        pytest.param(
            "observer", "get", "/supervisor/info", 200, "observer", id="observer-info"
        ),
        pytest.param(
            "observer", "post", "/supervisor/options", 403, None, id="observer-options"
        ),
        pytest.param(
            "observer",
            "post",
            "/addons/local_test/sys_options",
            403,
            None,
            id="observer-core-only",
        ),
        pytest.param("app", "get", "/addons/self/info", 200, "app", id="app-bypass"),
        pytest.param("app", "post", "/supervisor/options", 403, None, id="app-no-role"),
        pytest.param(
            "app",
            "post",
            "/addons/local_test/sys_options",
            403,
            None,
            id="app-core-only",
        ),
    ],
)
async def test_principal_access(
    call_api: CallAPI,
    principals: dict[str, CoreSysAttributes],
    transport: str,
    kind: str,
    method: str,
    path: str,
    status: int,
    request_from: str | None,
):
    """Test each principal gets the same access over a socket as with its token."""
    assert await call_api(transport, kind, method, path) == (
        status,
        principals.get(request_from),
    )


@pytest.mark.parametrize(
    "prefix", [pytest.param("", id="v1"), pytest.param("/v2", id="v2")]
)
@pytest.mark.parametrize(
    ("request_method", "request_path", "success_roles"), ROLE_PATHS
)
async def test_app_role_access_over_socket(
    call_api: CallAPI,
    principals: dict[str, CoreSysAttributes],
    prefix: str,
    request_method: str,
    request_path: str,
    success_roles: set[str],
):
    """Test an app on its socket gets exactly the access its role grants a token."""
    request_path = _versioned_path(prefix, request_path)
    app = principals["app"]
    for role in success_roles:
        app.data["hassio_role"] = role
        status, _ = await call_api("socket", "app", request_method, request_path)
        assert status == 200, role

    for role in set(ROLE_ALL) - success_roles:
        app.data["hassio_role"] = role
        status, _ = await call_api("socket", "app", request_method, request_path)
        assert status == 403, role


@pytest.mark.parametrize(
    ("kind", "path", "headers", "status", "request_from"),
    [
        pytest.param(
            "core",
            "/addons/local_test/sys_options",
            {"Authorization": "Bearer a_123456"},
            200,
            "core",
            id="app-token-on-core-socket",
        ),
        pytest.param(
            "core",
            "/addons/local_test/sys_options",
            {"Authorization": "Bearer garbage"},
            200,
            "core",
            id="garbage-token-on-core-socket",
        ),
        pytest.param(
            "app",
            "/addons/local_test/sys_options",
            {"Authorization": "Bearer h_123456"},
            403,
            None,
            id="core-token-on-app-socket",
        ),
        pytest.param(
            "app",
            "/addons/local_test/sys_options",
            {"X-Supervisor-Token": "h_123456"},
            403,
            None,
            id="core-token-header-on-app-socket",
        ),
    ],
)
async def test_socket_ignores_token(
    call_api: CallAPI,
    principals: dict[str, CoreSysAttributes],
    kind: str,
    path: str,
    headers: dict[str, str],
    status: int,
    request_from: str | None,
):
    """Test a token on a socket never changes who the caller is."""
    assert await call_api("socket", kind, "post", path, headers) == (
        status,
        principals.get(request_from),
    )


@pytest.mark.parametrize(
    ("transport", "request_from"),
    [pytest.param("token", None, id="tcp"), pytest.param("socket", "core", id="unix")],
)
async def test_passthrough_principal(
    call_api: CallAPI,
    principals: dict[str, CoreSysAttributes],
    transport: str,
    request_from: str | None,
):
    """Test paths without security check still know the caller on a socket."""
    assert await call_api(transport, "core", "get", "/supervisor/ping", {}) == (
        200,
        principals.get(request_from),
    )


@pytest.mark.parametrize("path", ["/core/api/hassio_auth", "/v2/core/api/hassio/app"])
async def test_blacklist_on_socket(call_api: CallAPI, path: str):
    """Test the blacklist applies to the socket principal too."""
    assert await call_api("socket", "core", "get", path) == (403, None)


async def test_unregistered_socket_rejected(
    coresys: CoreSys, tmp_run_dir: Path, principals: dict[str, CoreSysAttributes]
):
    """Test a connection outliving its socket registration is rejected."""
    api = RestAPI(coresys)
    app = web.Application(middlewares=[api.security.token_validation])
    app[RECORDED] = []
    app.router.add_route("*", "/{all:.*}", _recording_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    socket_path = tmp_run_dir / "core.sock"
    await api.sockets.register(principals["core"], socket_path, runner=runner)

    try:
        async with ClientSession(
            connector=UnixConnector(path=str(socket_path))
        ) as session:
            async with session.get("http://localhost/supervisor/info") as resp:
                assert resp.status == 200

            # The kept-alive connection stays open after the listener stops
            await api.sockets.unregister(socket_path)
            async with session.get("http://localhost/supervisor/info") as resp:
                assert resp.status == 403
    finally:
        await runner.cleanup()


async def test_dropped_connection_rejected(
    coresys: CoreSys, principals: dict[str, CoreSysAttributes]
):
    """Test a request whose connection is gone never falls back to its token."""
    api = RestAPI(coresys)
    request = make_mocked_request(
        "GET",
        "/supervisor/info",
        headers={"Authorization": "Bearer h_123456"},
        protocol=MagicMock(),
        transport=None,
    )
    handler = AsyncMock()

    with pytest.raises(web.HTTPForbidden):
        await api.security.token_validation(request, handler)

    handler.assert_not_called()


@pytest.mark.parametrize(
    ("socket_kinds", "tcp_kind", "issues"),
    [
        pytest.param(
            ["core"],
            "core",
            [
                Issue(
                    IssueType.DEPRECATED_TCP_API_REQUEST,
                    ContextType.CORE,
                    "/supervisor/info",
                )
            ],
            id="script",
        ),
        pytest.param([], "core", [], id="core-before-socket"),
        pytest.param(["app"], "core", [], id="core-after-app-socket"),
        pytest.param(["core"], "app", [], id="app"),
    ],
)
async def test_tcp_api_request_repair(
    call_api: CallAPI,
    coresys: CoreSys,
    socket_kinds: list[str],
    tcp_kind: str,
    issues: list[Issue],
):
    """Test Core's token over TCP raises a repair once Core has used its socket."""
    for kind in socket_kinds:
        await call_api("socket", kind, "get", "/addons/self/info")

    status, _ = await call_api("token", tcp_kind, "get", "/supervisor/info")

    assert status == 200
    assert coresys.resolution.issues == issues


async def test_tcp_api_request_repair_once(call_api: CallAPI, coresys: CoreSys):
    """Test the repair is raised once while each new path is logged once."""
    await call_api("socket", "core", "get", "/supervisor/info")
    with patch("supervisor.api.middleware.security._LOGGER") as logger:
        await call_api("token", "core", "get", "/supervisor/info")
        coresys.resolution.dismiss_issue(coresys.resolution.issues[0])
        await call_api("token", "core", "get", "/supervisor/info")
        await call_api("token", "core", "get", "/core/info")

    assert coresys.resolution.issues == []
    assert [call.args[1] for call in logger.warning.call_args_list] == [
        "/supervisor/info",
        "/core/info",
    ]
