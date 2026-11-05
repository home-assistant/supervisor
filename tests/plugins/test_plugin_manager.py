"""Test plugin manager."""

import asyncio
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface
from supervisor.exceptions import PluginError
from supervisor.plugins.audio import PluginAudio
from supervisor.plugins.base import PluginBase
from supervisor.plugins.cli import PluginCli
from supervisor.plugins.dns import PluginDns
from supervisor.plugins.multicast import PluginMulticast
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
    await coresys.updater.reload()

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


@pytest.mark.usefixtures("no_job_throttle")
async def test_load_skip_update_auto_update_disabled(
    coresys: CoreSys, mock_update_data: MockResponse, supervisor_internet: AsyncMock
):
    """Test plugin manager load skips updates when auto update is disabled."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    await coresys.updater.load()
    await coresys.updater.reload()

    coresys.updater.auto_update = False

    with (
        patch.object(DockerInterface, "attach") as attach,
        patch.object(DockerInterface, "update") as update,
        patch.object(Supervisor, "need_update", new=PropertyMock(return_value=False)),
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


async def test_shutdown_stops_plugins_in_parallel(coresys: CoreSys):
    """Test plugins are stopped in parallel."""
    stopped: list[str] = []
    all_stopping = asyncio.Barrier(4)

    async def _stop(plugin: PluginBase) -> None:
        async with asyncio.timeout(1):
            await all_stopping.wait()
        stopped.append(plugin.slug)

    with (
        patch.object(PluginCli, "stop", _stop),
        patch.object(PluginDns, "stop", _stop),
        patch.object(PluginAudio, "stop", _stop),
        patch.object(PluginMulticast, "stop", _stop),
    ):
        await coresys.plugins.shutdown()

    assert sorted(stopped) == ["audio", "cli", "dns", "multicast"]


async def test_shutdown_continues_after_error(
    coresys: CoreSys, capture_exception: Mock
):
    """Test a failing plugin does not keep the other plugins from stopping."""
    stopped: list[str] = []

    async def _stop(plugin: PluginBase) -> None:
        if plugin.slug == "dns":
            raise PluginError
        stopped.append(plugin.slug)

    with (
        patch.object(PluginCli, "stop", _stop),
        patch.object(PluginDns, "stop", _stop),
        patch.object(PluginAudio, "stop", _stop),
        patch.object(PluginMulticast, "stop", _stop),
    ):
        await coresys.plugins.shutdown()

    assert sorted(stopped) == ["audio", "cli", "multicast"]
    capture_exception.assert_called_once()
