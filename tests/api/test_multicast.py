"""Test multicast api."""


async def test_api_multicast_logs(advanced_logs_tester):
    """Test multicast logs."""
    await advanced_logs_tester("/multicast", "hassio_multicast")
