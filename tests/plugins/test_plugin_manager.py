"""Test plugin manager."""

from unittest.mock import patch

from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface


def mock_awaitable_bool(value: bool):
    """Return a mock of an awaitable bool."""

    async def _mock_bool(*args, **kwargs) -> bool:
        return value

    return _mock_bool


async def test_repair(coresys: CoreSys):
    """Test repair."""
    with patch.object(DockerInterface, "install") as install:
        # If instance exists, repair does nothing
        with patch.object(DockerInterface, "exists", new=mock_awaitable_bool(True)):
            await coresys.plugins.repair()

        install.assert_not_called()

        # If not, repair installs the image
        with patch.object(DockerInterface, "exists", new=mock_awaitable_bool(False)):
            await coresys.plugins.repair()

        assert install.call_count == len(coresys.plugins.all_plugins)
