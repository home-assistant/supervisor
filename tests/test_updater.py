"""Test updater files."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import ATTR_HASSOS_UNRESTRICTED, BusEvent
from supervisor.coresys import CoreSys
from supervisor.dbus.const import ConnectivityState
from supervisor.exceptions import UpdaterJobError
from supervisor.jobs import SupervisorJob
from supervisor.resolution.const import UnsupportedReason

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
    await coresys.updater.reload()
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


@pytest.mark.usefixtures("no_job_throttle")
async def test_load_calls_reload_when_os_board_without_version(
    coresys: CoreSys, mock_update_data: MockResponse, supervisor_internet: AsyncMock
) -> None:
    """Test load calls reload when OS board exists but no version_hassos_unrestricted."""
    # Set up OS board but no version data
    coresys.os._board = "rpi4"  # pylint: disable=protected-access
    coresys.security.force = True

    # Mock reload to verify it gets called
    with patch.object(coresys.updater, "reload", new_callable=AsyncMock) as mock_reload:
        await coresys.updater.load()
        mock_reload.assert_called_once()


@pytest.mark.usefixtures("no_job_throttle")
async def test_load_skips_reload_when_os_board_with_version(
    coresys: CoreSys, mock_update_data: MockResponse, supervisor_internet: AsyncMock
) -> None:
    """Test load skips reload when OS board exists and version_hassos_unrestricted is set."""
    # Set up OS board and version data
    coresys.os._board = "rpi4"  # pylint: disable=protected-access
    coresys.security.force = True

    # Pre-populate version_hassos_unrestricted by setting it directly on the data dict
    # Use the same approach as other tests that modify internal state
    coresys.updater._data[ATTR_HASSOS_UNRESTRICTED] = AwesomeVersion("13.1")  # pylint: disable=protected-access

    # Mock reload to verify it doesn't get called
    with patch.object(coresys.updater, "reload", new_callable=AsyncMock) as mock_reload:
        await coresys.updater.load()
        mock_reload.assert_not_called()


@pytest.mark.usefixtures("no_job_throttle")
async def test_load_skips_reload_when_no_os_board(
    coresys: CoreSys, mock_update_data: MockResponse, supervisor_internet: AsyncMock
) -> None:
    """Test load skips reload when no OS board is set."""
    # Ensure no OS board is set
    coresys.os._board = None  # pylint: disable=protected-access

    # Mock reload to verify it doesn't get called
    with patch.object(coresys.updater, "reload", new_callable=AsyncMock) as mock_reload:
        await coresys.updater.load()
        mock_reload.assert_not_called()


async def test_fetch_data_no_update_when_os_unsupported(
    coresys: CoreSys, websession: MagicMock
) -> None:
    """Test that fetch_data doesn't update data when OS is unsupported."""
    # Store initial versions to compare later
    initial_supervisor_version = coresys.updater.version_supervisor
    initial_homeassistant_version = coresys.updater.version_homeassistant
    initial_hassos_version = coresys.updater.version_hassos

    coresys.websession.head = AsyncMock()

    # Mark OS as unsupported by adding UnsupportedReason.OS_VERSION
    coresys.resolution.unsupported.append(UnsupportedReason.OS_VERSION)

    # Attempt to fetch data should fail due to OS_SUPPORTED condition
    with pytest.raises(
        UpdaterJobError, match="blocked from execution, unsupported OS version"
    ):
        await coresys.updater.fetch_data()

    # Verify that versions were not updated
    assert coresys.updater.version_supervisor == initial_supervisor_version
    assert coresys.updater.version_homeassistant == initial_homeassistant_version
    assert coresys.updater.version_hassos == initial_hassos_version
