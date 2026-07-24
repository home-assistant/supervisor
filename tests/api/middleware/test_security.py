"""Test API security layer."""

import asyncio
from http import HTTPStatus
from unittest.mock import patch

from aiohttp import web
from aiohttp.test_utils import TestClient
import pytest
import urllib3

from supervisor.api import RestAPI
from supervisor.apps.app import App
from supervisor.const import ROLE_ALL, CoreState
from supervisor.coresys import CoreSys

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
async def api_token_validation(aiohttp_client, coresys: CoreSys) -> TestClient:
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

    return await aiohttp_client(api.webapp)


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


@pytest.mark.parametrize(
    ("request_method", "request_path", "success_roles"),
    [
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
        ("post", "/addons/self/sys_options", set()),
        ("post", "/addons/abc123/sys_options", set()),
    ],
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
