"""Test updater files."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import BusEvent
from supervisor.coresys import CoreSys
from supervisor.dbus.const import ConnectivityState
from supervisor.jobs import SupervisorJob

from tests.common import MockResponse, load_binary_fixture
from tests.dbus_service_mocks.network_manager import (
    NetworkManager as NetworkManagerService,
)

URL_TEST = "https://version.home-assistant.io/stable.json"


@pytest.mark.usefixtures("no_job_throttle")
async def test_fetch_versions(
    coresys: CoreSys, mock_update_data: MockResponse, supervisor_internet: AsyncMock
) -> None:
    """Test download and sync version."""

    coresys.security.force = True
    await coresys.updater.fetch_data()

    data = json.loads(await mock_update_data.text())
    assert coresys.updater.version_supervisor == data["supervisor"]
    assert coresys.updater.version_homeassistant == data["homeassistant"]["default"]

    assert coresys.updater.version_audio == data["audio"]
    assert coresys.updater.version_cli == data["cli"]
    assert coresys.updater.version_dns == data["dns"]
    assert coresys.updater.version_multicast == data["multicast"]
    assert coresys.updater.version_observer == data["observer"]

    assert coresys.updater.image_homeassistant == data["images"]["core"].format(
        machine=coresys.machine
    )

    assert coresys.updater.image_supervisor == data["images"]["supervisor"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_cli == data["images"]["cli"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_audio == data["images"]["audio"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_dns == data["images"]["dns"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_observer == data["images"]["observer"].format(
        arch=coresys.arch.supervisor
    )
    assert coresys.updater.image_multicast == data["images"]["multicast"].format(
        arch=coresys.arch.supervisor
    )


@pytest.mark.usefixtures("no_job_throttle")
@pytest.mark.parametrize(
    "version, expected",
    [
        ("3.1", "3.13"),
        ("4.5", "4.20"),
        ("5.0", "5.13"),
        ("6.4", "6.6"),
        ("4.20", "5.13"),
    ],
)
async def test_os_update_path(
    coresys: CoreSys,
    version: str,
    expected: str,
    mock_update_data: AsyncMock,
    supervisor_internet: AsyncMock,
):
    """Test OS upgrade path across major versions."""
    coresys.os._board = "rpi4"  # pylint: disable=protected-access
    coresys.os._version = AwesomeVersion(version)  # pylint: disable=protected-access
    with patch.object(type(coresys.security), "verify_own_content"):
        await coresys.updater.fetch_data()

        assert coresys.updater.version_hassos == AwesomeVersion(expected)


@pytest.mark.usefixtures("no_job_throttle")
async def test_delayed_fetch_for_connectivity(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    websession: MagicMock,
):
    """Test initial version fetch waits for connectivity on load."""
    coresys.websession.get = MagicMock()
    coresys.websession.get.return_value.__aenter__.return_value.status = 200
    coresys.websession.get.return_value.__aenter__.return_value.read.return_value = (
        load_binary_fixture("version_stable.json")
    )
    coresys.websession.head = AsyncMock()
    coresys.security.verify_own_content = AsyncMock()

    # Network connectivity change causes a series of async tasks to eventually do a version fetch
    # Rather then use some kind of sleep loop, set up listener for start of fetch data job
    event = asyncio.Event()

    async def find_fetch_data_job_start(job: SupervisorJob):
        if job.name == "updater_fetch_data":
            event.set()

    coresys.bus.register_event(BusEvent.SUPERVISOR_JOB_START, find_fetch_data_job_start)

    # Start with no connectivity and confirm there is no version fetch on load
    coresys.supervisor.connectivity = False
    network_manager_service.connectivity = ConnectivityState.CONNECTIVITY_NONE.value
    await coresys.host.network.load()
    await coresys.host.network.check_connectivity()

    await coresys.updater.load()
    coresys.websession.get.assert_not_called()

    # Now signal host has connectivity and wait for fetch data to complete to assert
    network_manager_service.emit_properties_changed(
        {"Connectivity": ConnectivityState.CONNECTIVITY_FULL}
    )
    await network_manager_service.ping()
    async with asyncio.timeout(5):
        await event.wait()
    await asyncio.sleep(0)

    coresys.websession.get.assert_called_once()
    assert (
        coresys.websession.get.call_args[0][0]
        == "https://version.home-assistant.io/stable.json"
    )
