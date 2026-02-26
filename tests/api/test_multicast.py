"""Test multicast api."""

from supervisor.host.const import LogFormatter


async def test_api_multicast_logs(advanced_logs_tester):
    """Test multicast logs."""
    await advanced_logs_tester("/multicast", "hassio_multicast", LogFormatter.VERBOSE)
