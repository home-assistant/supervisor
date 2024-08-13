"""Test docker stats."""

import pytest

from supervisor.docker.stats import DockerStats

from tests.common import load_json_fixture


@pytest.mark.parametrize(
    "stats_mock",
    ["container_stats", "container_stats_cgroupv1", "container_stats_cgroupv2"],
)
def test_cpu_percentage(stats_mock: str):
    """Test CPU percentage."""
    stats_fixture = load_json_fixture(f"{stats_mock}.json")
    stats = DockerStats(stats_fixture)

    stats._calc_cpu_percent(stats_fixture)  # pylint: disable=protected-access
    assert stats.cpu_percent == 90.0

    stats_fixture["cpu_stats"]["cpu_usage"]["total_usage"] = 0
    stats_fixture["precpu_stats"]["cpu_usage"]["total_usage"] = 0
    stats_fixture["cpu_stats"]["system_cpu_usage"] = 0
    stats_fixture["precpu_stats"]["system_cpu_usage"] = 0
    stats._calc_cpu_percent(stats_fixture)  # pylint: disable=protected-access
    assert stats.cpu_percent == 0.0


@pytest.mark.parametrize(
    "stats_mock",
    ["container_stats", "container_stats_cgroupv1", "container_stats_cgroupv2"],
)
async def test_memory_usage(stats_mock: str):
    """Test memory usage calculation."""
    stats_fixture = load_json_fixture(f"{stats_mock}.json")
    stats = DockerStats(stats_fixture)

    assert stats.memory_limit == 4000000000
    assert stats.memory_usage == 59700000
    assert stats.memory_percent == 1.49
