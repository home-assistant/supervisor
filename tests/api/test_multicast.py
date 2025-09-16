"""Test multicast api."""

from unittest.mock import MagicMock

from aiohttp.test_utils import TestClient

from supervisor.coresys import CoreSys

from tests.api import common_test_api_advanced_logs


async def test_api_multicast_logs(
    api_client: TestClient, journald_logs: MagicMock, coresys: CoreSys, os_available
):
    """Test multicast logs."""
    await common_test_api_advanced_logs(
        "/multicast",
        "hassio_multicast",
        api_client,
        journald_logs,
        coresys,
        os_available,
    )
