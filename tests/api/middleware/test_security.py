"""Test API security layer."""
from http import HTTPStatus
from unittest.mock import patch

from aiohttp import web
import pytest
import urllib3

from supervisor.api import RestAPI
from supervisor.const import CoreState
from supervisor.coresys import CoreSys

# pylint: disable=redefined-outer-name


async def mock_handler(request):
    """Return OK."""
    return web.Response(text="OK")


@pytest.fixture
async def api_system(aiohttp_client, run_dir, coresys: CoreSys):
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


@pytest.mark.asyncio
async def test_api_security_system_initialize(api_system, coresys: CoreSys):
    """Test security."""
    coresys.core.state = CoreState.INITIALIZE

    resp = await api_system.get("/supervisor/ping")
    result = await resp.json()
    assert resp.status == 400
    assert result["result"] == "error"


@pytest.mark.asyncio
async def test_api_security_system_setup(api_system, coresys: CoreSys):
    """Test security."""
    coresys.core.state = CoreState.SETUP

    resp = await api_system.get("/supervisor/ping")
    result = await resp.json()
    assert resp.status == 400
    assert result["result"] == "error"


@pytest.mark.asyncio
async def test_api_security_system_running(api_system, coresys: CoreSys):
    """Test security."""
    coresys.core.state = CoreState.RUNNING

    resp = await api_system.get("/supervisor/ping")
    assert resp.status == 200


@pytest.mark.asyncio
async def test_api_security_system_startup(api_system, coresys: CoreSys):
    """Test security."""
    coresys.core.state = CoreState.STARTUP

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
    request_path,
    request_params,
    fail_on_query_string,
    api_system,
    caplog: pytest.LogCaptureFixture,
    loop,
) -> None:
    """Test request paths that should be filtered."""

    # Manual params handling
    if request_params:
        raw_params = "&".join(f"{val}={key}" for val, key in request_params.items())
        man_params = f"?{raw_params}"
    else:
        man_params = ""

    http = urllib3.PoolManager()
    resp = await loop.run_in_executor(
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
