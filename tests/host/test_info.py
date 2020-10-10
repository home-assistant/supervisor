"""Test host info."""
from unittest.mock import patch

from supervisor.host.info import InfoCenter


def test_host_free_space(coresys):
    """Test host free space."""
    info = InfoCenter(coresys)
    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0 ** 3))):
        free = info.free_space

    assert free == 2.0
