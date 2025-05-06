"""Test plugin manager."""

from unittest.mock import AsyncMock, PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface
from supervisor.plugins.base import PluginBase
from supervisor.supervisor import Supervisor

from tests.common import MockResponse


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


@pytest.mark.usefixtures("no_job_throttle")
async def test_load(
    coresys: CoreSys, mock_update_data: MockResponse, supervisor_internet: AsyncMock
):
    """Test plugin manager load."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    await coresys.updater.load()

    need_update = PropertyMock(return_value=True)
    with (
        patch.object(DockerInterface, "attach") as attach,
        patch.object(DockerInterface, "update") as update,
        patch.object(Supervisor, "need_update", new=need_update),
        patch.object(PluginBase, "need_update", new=PropertyMock(return_value=True)),
        patch.object(
            PluginBase,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("1970-01-01")),
        ),
    ):
        await coresys.plugins.load()

        assert attach.call_count == 5
        update.assert_not_called()

        need_update.return_value = False
        await coresys.plugins.load()

        assert attach.call_count == 10
        assert update.call_count == 5
