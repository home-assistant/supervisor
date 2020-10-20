"""Test docker stats."""
from supervisor.docker.stats import DockerStats

from tests.common import load_json_fixture


def test_cpu_presentage(docker):
    """Test CPU presentage."""
    stats_fixtrue = load_json_fixture("container_stats.json")
    stats = DockerStats(stats_fixtrue)

    stats._calc_cpu_percent(stats_fixtrue)  # pylint: disable=protected-access
    assert stats.cpu_percent == 90.0

    stats_fixtrue["cpu_stats"]["cpu_usage"]["total_usage"] = 0
    stats_fixtrue["precpu_stats"]["cpu_usage"]["total_usage"] = 0
    stats_fixtrue["cpu_stats"]["system_cpu_usage"] = 0
    stats_fixtrue["precpu_stats"]["system_cpu_usage"] = 0
    stats._calc_cpu_percent(stats_fixtrue)  # pylint: disable=protected-access
    assert stats.cpu_percent == 0.0
