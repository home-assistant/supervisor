"""Test API security layer."""

import asyncio
from http import HTTPStatus
from unittest.mock import patch

from aiohttp import web
from aiohttp.test_utils import TestClient
import pytest
import urllib3

from supervisor.addons.addon import Addon
from supervisor.api import RestAPI
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

    yield await aiohttp_client(api.webapp)


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

    yield await aiohttp_client(api.webapp)


@pytest.mark.asyncio
async def test_api_security_system_initialize(api_system: TestClient, coresys: CoreSys):
    """Test security."""
    await coresys.core.set_state(CoreState.INITIALIZE)

    resp = await api_system.get("/supervisor/ping")
    result = await resp.json()
    assert resp.status == 400
    assert result["result"] == "error"


@pytest.mark.asyncio
async def test_api_security_system_setup(api_system: TestClient, coresys: CoreSys):
    """Test security."""
    await coresys.core.set_state(CoreState.SETUP)

    resp = await api_system.get("/supervisor/ping")
    result = await resp.json()
    assert resp.status == 400
    assert result["result"] == "error"


@pytest.mark.asyncio
async def test_api_security_system_running(api_system: TestClient, coresys: CoreSys):
    """Test security."""
    await coresys.core.set_state(CoreState.RUNNING)

    resp = await api_system.get("/supervisor/ping")
    assert resp.status == 200


@pytest.mark.asyncio
async def test_api_security_system_startup(api_system: TestClient, coresys: CoreSys):
    """Test security."""
    await coresys.core.set_state(CoreState.STARTUP)

    resp = await api_system.get("/supervisor/ping")
    assert resp.status == 200


@pytest.mark.asyncio
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
    "request_method,request_path,success_roles",
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
async def test_token_validation(
    api_token_validation: TestClient,
    install_addon_example: Addon,
    request_method: str,
    request_path: str,
    success_roles: set[str],
):
    """Test token validation paths."""
    install_addon_example.persist["access_token"] = "abc123"
    install_addon_example.data["hassio_api"] = True
    for role in success_roles:
        install_addon_example.data["hassio_role"] = role
        resp = await getattr(api_token_validation, request_method)(
            request_path, headers={"Authorization": "Bearer abc123"}
        )
        assert resp.status == 200

    for role in set(ROLE_ALL) - success_roles:
        install_addon_example.data["hassio_role"] = role
        resp = await getattr(api_token_validation, request_method)(
            request_path, headers={"Authorization": "Bearer abc123"}
        )
        assert resp.status == 403


async def test_home_assistant_paths(api_token_validation: TestClient, coresys: CoreSys):
    """Test Home Assistant only paths."""
    coresys.homeassistant.supervisor_token = "abc123"
    resp = await api_token_validation.post(
        "/addons/local_test/sys_options", headers={"Authorization": "Bearer abc123"}
    )
    assert resp.status == 200
