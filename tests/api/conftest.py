"""Fixtures for API tests."""

from collections.abc import Awaitable, Callable
from unittest.mock import ANY, AsyncMock, MagicMock

from aiohttp import web
from aiohttp.test_utils import TestClient
import pytest

from supervisor.api import RestAPI
from supervisor.const import REQUEST_FROM, FeatureFlag
from supervisor.coresys import CoreSys
from supervisor.host.const import LogFormat, LogFormatter

DEFAULT_LOG_RANGE = "entries=:-99:100"
DEFAULT_LOG_RANGE_FOLLOW = "entries=:-99:18446744073709551615"


async def _common_test_api_advanced_logs(
    path_prefix: str,
    syslog_identifier: str,
    formatter: LogFormatter,
    api_client: TestClient,
    journald_logs: MagicMock,
    coresys: CoreSys,
    os_available: None,
    journal_logs_reader: MagicMock,
):
    """Template for tests of endpoints using advanced logs."""
    resp = await api_client.get(f"{path_prefix}/logs")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": syslog_identifier},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )
    journal_logs_reader.assert_called_with(ANY, formatter, False)

    journald_logs.reset_mock()
    journal_logs_reader.reset_mock()

    resp = await api_client.get(f"{path_prefix}/logs?no_colors")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": syslog_identifier},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )
    journal_logs_reader.assert_called_with(ANY, formatter, True)

    journald_logs.reset_mock()
    journal_logs_reader.reset_mock()

    resp = await api_client.get(f"{path_prefix}/logs/follow")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": syslog_identifier, "follow": ""},
        range_header=DEFAULT_LOG_RANGE_FOLLOW,
        accept=LogFormat.JOURNAL,
    )
    journal_logs_reader.assert_called_with(ANY, formatter, False)

    journald_logs.reset_mock()
    journal_logs_reader.reset_mock()

    mock_response = MagicMock()
    mock_response.text = AsyncMock(
        return_value='{"CONTAINER_LOG_EPOCH": "12345"}\n{"CONTAINER_LOG_EPOCH": "12345"}\n'
    )
    journald_logs.return_value.__aenter__.return_value = mock_response

    resp = await api_client.get(f"{path_prefix}/logs/latest")
    assert resp.status == 200

    assert journald_logs.call_count == 2

    # Check the first call for getting epoch
    epoch_call = journald_logs.call_args_list[0]
    assert epoch_call[1]["params"] == {"CONTAINER_NAME": syslog_identifier}
    assert epoch_call[1]["range_header"] == "entries=:-1:2"

    # Check the second call for getting logs with the epoch
    logs_call = journald_logs.call_args_list[1]
    assert logs_call[1]["params"]["SYSLOG_IDENTIFIER"] == syslog_identifier
    assert logs_call[1]["params"]["CONTAINER_LOG_EPOCH"] == "12345"
    assert logs_call[1]["range_header"] == "entries=:0:18446744073709551615"
    journal_logs_reader.assert_called_with(ANY, formatter, True)

    journald_logs.reset_mock()
    journal_logs_reader.reset_mock()

    resp = await api_client.get(f"{path_prefix}/logs/boots/0")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={"SYSLOG_IDENTIFIER": syslog_identifier, "_BOOT_ID": "ccc"},
        range_header=DEFAULT_LOG_RANGE,
        accept=LogFormat.JOURNAL,
    )

    journald_logs.reset_mock()

    resp = await api_client.get(f"{path_prefix}/logs/boots/0/follow")
    assert resp.status == 200
    assert resp.content_type == "text/plain"

    journald_logs.assert_called_once_with(
        params={
            "SYSLOG_IDENTIFIER": syslog_identifier,
            "_BOOT_ID": "ccc",
            "follow": "",
        },
        range_header=DEFAULT_LOG_RANGE_FOLLOW,
        accept=LogFormat.JOURNAL,
    )


@pytest.fixture
async def advanced_logs_tester(
    api_client: TestClient,
    journald_logs: MagicMock,
    coresys: CoreSys,
    os_available,
    journal_logs_reader: MagicMock,
) -> Callable[..., Awaitable[None]]:
    """Fixture that returns a function to test advanced logs endpoints.

    This allows tests to avoid explicitly passing all the required fixtures.

    Usage:
        async def test_my_logs(advanced_logs_tester):
            await advanced_logs_tester("/path/prefix", "syslog_identifier")
    """

    async def test_logs(
        path_prefix: str,
        syslog_identifier: str,
        formatter: LogFormatter = LogFormatter.PLAIN,
    ):
        await _common_test_api_advanced_logs(
            path_prefix,
            syslog_identifier,
            formatter,
            api_client,
            journald_logs,
            coresys,
            os_available,
            journal_logs_reader,
        )

    return test_logs


@pytest.fixture
async def api_client_v2(aiohttp_client, coresys: CoreSys) -> TestClient:
    """Fixture for RestAPI client with v2 API enabled."""
    coresys.config.set_feature_flag(FeatureFlag.SUPERVISOR_V2_API, True)

    @web.middleware
    async def _security_middleware(request: web.Request, handler: web.RequestHandler):
        request[REQUEST_FROM] = coresys.homeassistant
        return await handler(request)

    api = RestAPI(coresys)
    api.webapp = web.Application(middlewares=[_security_middleware])
    api.start = AsyncMock()
    await api.load()
    yield await aiohttp_client(api.webapp)


@pytest.fixture(params=[pytest.param("", id="v1"), pytest.param("/v2", id="v2")])
async def api_client_with_prefix(
    request: pytest.FixtureRequest,
    api_client: TestClient,
    api_client_v2: TestClient,
) -> tuple[TestClient, str]:
    """Fixture providing (client, path_prefix) for both v1 and v2 API paths.

    Use this for APIs whose behavior is identical between v1 and v2 to confirm
    both versions work correctly.
    """
    if request.param == "":
        return api_client, ""
    return api_client_v2, "/v2"


@pytest.fixture(
    params=[pytest.param("/addons", id="v1"), pytest.param("/v2/apps", id="v2")]
)
async def app_api_client_with_root(
    request: pytest.FixtureRequest,
    api_client: TestClient,
    api_client_v2: TestClient,
) -> tuple[TestClient, str]:
    """Fixture providing (client, path_root) for both v1 and v2 app management paths.

    v1 root: /addons/{slug}/...
    v2 root: /v2/apps/{slug}/...
    """
    root: str = request.param
    client = api_client if root == "/addons" else api_client_v2
    return client, root


@pytest.fixture(
    params=[
        pytest.param("store/addons", id="v1"),
        pytest.param("v2/store/apps", id="v2"),
    ]
)
async def store_app_api_client_with_root(
    request: pytest.FixtureRequest,
    api_client: TestClient,
    api_client_v2: TestClient,
) -> tuple[TestClient, str]:
    """Fixture providing (client, resource_root) for both v1 and v2 store app paths.

    v1 root: store/addons/{slug}/...
    v2 root: v2/store/apps/{slug}/...
    """
    resource: str = request.param
    client = api_client_v2 if resource.startswith("v2/") else api_client
    return client, resource
