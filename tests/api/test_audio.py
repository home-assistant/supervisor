"""Test audio api."""

from unittest.mock import MagicMock

from aiohttp.test_utils import TestClient

from tests.api import common_test_api_advanced_logs


async def test_api_audio_logs(api_client: TestClient, journald_logs: MagicMock):
    """Test audio logs."""
    await common_test_api_advanced_logs(
        "/audio", "hassio_audio", api_client, journald_logs
    )
