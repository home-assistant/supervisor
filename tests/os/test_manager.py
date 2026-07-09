"""Test Home Assistant OS functionality."""

from pathlib import Path
from unittest.mock import AsyncMock, PropertyMock, call, patch

from awesomeversion import AwesomeVersion
from dbus_fast import Variant
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.dbus.const import RaucState
from supervisor.exceptions import HassOSJobError, HassOSUpdateError
from supervisor.resolution.const import (
    ContextType,
    IssueType,
    SuggestionType,
    UnhealthyReason,
)

from tests.common import MockResponse
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.rauc import Rauc as RaucService

# pylint: disable=protected-access


@pytest.mark.usefixtures("no_job_throttle")
async def test_ota_url_generic_x86_64_rename(
    coresys: CoreSys, mock_update_data: MockResponse, supervisor_internet: AsyncMock
) -> None:
    """Test download URL generated."""
    coresys.os._board = "intel-nuc"
    coresys.os._version = AwesomeVersion("5.13")
    await coresys.updater.fetch_data()

    version6 = AwesomeVersion("6.0")
    url = coresys.updater.ota_url.format(
        version=str(version6), board="generic-x86-64", os_name="haos"
    )

    assert coresys.os._get_download_url(version6) == url


def test_ota_url_os_name(coresys: CoreSys) -> None:
    """Test download URL generated with os_name."""
    board = "generic-x86-64"
    os_name = "haos"
    versionstr = "6.0"

    url = "https://github.com/home-assistant/operating-system/releases/download/{version}/{os_name}_{board}-{version}.raucb"
    url_formatted = url.format(version=versionstr, board=board, os_name=os_name)

    coresys.os._board = board
    coresys.os._os_name = os_name
    coresys.updater._data = {"ota": url}

    url = coresys.os._get_download_url(AwesomeVersion(versionstr))
    assert url == url_formatted


def test_ota_url_os_name_rel_5_downgrade(coresys: CoreSys) -> None:
    """Test download URL generated with os_name."""
    board = "generic-x86-64"
    versionstr = "5.9"

    # On downgrade below 6.0 we need to use hassos as os_name.
    url = "https://github.com/home-assistant/operating-system/releases/download/{version}/{os_name}_{board}-{version}.raucb"
    url_formatted = url.format(version=versionstr, board=board, os_name="hassos")

    coresys.os._board = board
    coresys.os._os_name = "haos"
    coresys.updater._data = {"ota": url}

    url = coresys.os._get_download_url(AwesomeVersion(versionstr))
    assert url == url_formatted


async def test_update_fails_if_out_of_date(
    coresys: CoreSys, supervisor_internet: AsyncMock
) -> None:
    """Test update of OS fails if Supervisor is out of date."""
    await coresys.core.set_state(CoreState.RUNNING)
    with (
        patch.object(
            type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
        ),
        patch.object(
            type(coresys.os), "available", new=PropertyMock(return_value=True)
        ),
        pytest.raises(HassOSJobError),
    ):
        await coresys.os.update()


async def test_update_fails_if_unhealthy(
    coresys: CoreSys,
) -> None:
    """Test update of OS fails if Supervisor is unhealthy."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.resolution.add_unhealthy_reason(UnhealthyReason.DUPLICATE_OS_INSTALLATION)
    with (
        patch.object(
            type(coresys.os), "available", new=PropertyMock(return_value=True)
        ),
        pytest.raises(HassOSJobError),
    ):
        await coresys.os.update()


async def test_update_success_cleans_up_bundle(
    coresys: CoreSys,
    tmp_supervisor_data: Path,
    path_extern: None,
    supervisor_internet: AsyncMock,
) -> None:
    """Test successful OS update installs via RAUC and removes the downloaded bundle."""
    await coresys.core.set_state(CoreState.RUNNING)

    coresys.os._available = True
    coresys.os._board = "generic-x86-64"
    coresys.os._os_name = "haos"
    coresys.os._version = AwesomeVersion("12.0")
    coresys.updater._data = {
        "ota": (
            "https://github.com/home-assistant/operating-system/releases/download/"
            "{version}/{os_name}_{board}-{version}.raucb"
        ),
        "hassos_unrestricted": AwesomeVersion("13.0"),
    }

    async def fake_download(url: str, raucb: Path) -> None:
        raucb.touch()

    reboot_mock = AsyncMock()

    with (
        patch.object(coresys.os, "_download_raucb", side_effect=fake_download),
        patch.object(coresys.host.control, "reboot", reboot_mock),
    ):
        await coresys.os.update()

    bundle = coresys.config.path_tmp / "hassos-13.0.raucb"
    assert not bundle.exists()
    reboot_mock.assert_not_called()
    assert (
        IssueType.REBOOT_REQUIRED,
        ContextType.SYSTEM,
    ) in {(issue.type, issue.context) for issue in coresys.resolution.issues}
    assert (
        SuggestionType.EXECUTE_REBOOT,
        ContextType.SYSTEM,
    ) in {
        (suggestion.type, suggestion.context)
        for suggestion in coresys.resolution.suggestions
    }
    assert coresys.os.version_pending == AwesomeVersion("13.0")
    assert coresys.os.need_update is False


async def test_update_pending_version_blocked(
    coresys: CoreSys,
    tmp_supervisor_data: Path,
    path_extern: None,
    supervisor_internet: AsyncMock,
) -> None:
    """Test updating to an already installed version pending reboot is rejected."""
    await coresys.core.set_state(CoreState.RUNNING)

    coresys.os._available = True
    coresys.os._board = "generic-x86-64"
    coresys.os._os_name = "haos"
    coresys.os._version = AwesomeVersion("12.0")
    coresys.updater._data = {
        "ota": (
            "https://github.com/home-assistant/operating-system/releases/download/"
            "{version}/{os_name}_{board}-{version}.raucb"
        ),
        "hassos_unrestricted": AwesomeVersion("13.0"),
    }

    async def fake_download(url: str, raucb: Path) -> None:
        raucb.touch()

    with patch.object(
        coresys.os, "_download_raucb", side_effect=fake_download
    ) as download:
        await coresys.os.update()

        with pytest.raises(HassOSUpdateError):
            await coresys.os.update()

    download.assert_called_once()


async def test_mark_healthy_keeps_pending_update(coresys: CoreSys) -> None:
    """Test mark_healthy does not mark booted slot active with pending update."""
    coresys.os._available = True
    coresys.os._version_pending = AwesomeVersion("13.0")

    with patch.object(
        coresys.dbus.rauc,
        "mark",
        AsyncMock(return_value=["kernel.1", "marked slot kernel.1 as good"]),
    ) as mark:
        await coresys.os.mark_healthy()

    mark.assert_called_once_with(RaucState.GOOD, "booted")


async def test_mark_healthy_marks_active_without_pending(coresys: CoreSys) -> None:
    """Test mark_healthy marks booted slot good and active without pending update."""
    coresys.os._available = True

    with patch.object(
        coresys.dbus.rauc,
        "mark",
        AsyncMock(return_value=["kernel.1", "marked slot kernel.1 as good"]),
    ) as mark:
        await coresys.os.mark_healthy()

    assert mark.call_args_list == [
        call(RaucState.GOOD, "booted"),
        call(RaucState.ACTIVE, "booted"),
    ]


async def test_board_name_supervised(coresys: CoreSys) -> None:
    """Test board name is supervised when not on haos."""
    with patch("supervisor.os.manager.CPE.get_product", return_value=["not-hassos"]):
        await coresys.dbus.hostname.connect(coresys.dbus.bus)
        await coresys.os.load()
        assert coresys.os.board == "supervised"


async def test_load_slot_status_fresh_install(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> None:
    """Test load works when slot status returns minimal fresh install response."""
    rauc_service: RaucService = all_dbus_services["rauc"]
    rauc_service.response_get_slot_status = [
        (
            "kernel.0",
            {
                "class": Variant("s", "kernel"),
                "boot-status": Variant("s", "good"),
                "type": Variant("s", "raw"),
                "bootname": Variant("s", "A"),
                "device": Variant("s", "/dev/disk/by-partlabel/hassos-kernel0"),
                "state": Variant("s", "inactive"),
            },
        ),
        (
            "boot.0",
            {
                "bundle.compatible": Variant("s", "haos-green"),
                "sha256": Variant(
                    "s",
                    "f0b8a08d9bc49acbb230cf709beb0aa214cbee09969566755dff52fb8b3cc29b",
                ),
                "state": Variant("s", "inactive"),
                "size": Variant("t", 16777216),
                "installed.count": Variant("u", 1),
                "class": Variant("s", "boot"),
                "device": Variant("s", "/dev/disk/by-partlabel/hassos-boot"),
                "type": Variant("s", "vfat"),
                "status": Variant("s", "ok"),
                "bundle.version": Variant("s", "12.2.dev20240313"),
                "installed.timestamp": Variant("s", "2024-03-15T17:27:38Z"),
            },
        ),
        (
            "rootfs.0",
            {
                "class": Variant("s", "rootfs"),
                "parent": Variant("s", "kernel.0"),
                "type": Variant("s", "raw"),
                "state": Variant("s", "inactive"),
                "device": Variant("s", "/dev/disk/by-partlabel/hassos-system0"),
            },
        ),
        (
            "spl.0",
            {
                "bundle.compatible": Variant("s", "haos-green"),
                "sha256": Variant(
                    "s",
                    "97e4f1616250e7f9d2b20d98a972cf3aab03849a8cf50a8630f96a183b64384f",
                ),
                "state": Variant("s", "inactive"),
                "size": Variant("t", 16777216),
                "installed.count": Variant("u", 1),
                "class": Variant("s", "spl"),
                "device": Variant("s", "/dev/disk/by-partlabel/hassos-boot"),
                "type": Variant("s", "raw"),
                "status": Variant("s", "ok"),
                "bundle.version": Variant("s", "12.2.dev20240313"),
                "installed.timestamp": Variant("s", "2024-03-15T17:27:47Z"),
            },
        ),
        (
            "kernel.1",
            {
                "activated.count": Variant("u", 1),
                "activated.timestamp": Variant("s", "2024-03-15T17:27:47Z"),
                "boot-status": Variant("s", "good"),
                "bundle.compatible": Variant("s", "haos-green"),
                "sha256": Variant(
                    "s",
                    "c327b3c2ac4f56926d0d7c4693fe79c67dc05ed49c4abd020da981bf4faf977f",
                ),
                "state": Variant("s", "booted"),
                "size": Variant("t", 13410304),
                "installed.count": Variant("u", 1),
                "class": Variant("s", "kernel"),
                "device": Variant("s", "/dev/disk/by-partlabel/hassos-kernel1"),
                "type": Variant("s", "raw"),
                "bootname": Variant("s", "B"),
                "bundle.version": Variant("s", "12.2.dev20240313"),
                "installed.timestamp": Variant("s", "2024-03-15T17:27:39Z"),
                "status": Variant("s", "ok"),
            },
        ),
        (
            "rootfs.1",
            {
                "bundle.compatible": Variant("s", "haos-green"),
                "parent": Variant("s", "kernel.1"),
                "state": Variant("s", "active"),
                "size": Variant("t", 194560000),
                "sha256": Variant(
                    "s",
                    "151dbfff469a7f1252cb8482e7a9439c5164f52c53ed141e377c10e6858208cb",
                ),
                "class": Variant("s", "rootfs"),
                "device": Variant("s", "/dev/disk/by-partlabel/hassos-system1"),
                "type": Variant("s", "raw"),
                "status": Variant("s", "ok"),
                "bundle.version": Variant("s", "12.2.dev20240313"),
                "installed.timestamp": Variant("s", "2024-03-15T17:27:45Z"),
                "installed.count": Variant("u", 1),
            },
        ),
    ]

    await coresys.os.load()
    assert len(coresys.os.slots) == 6
    assert coresys.os.get_slot_name("A") == "kernel.0"
    assert coresys.os.get_slot_name("B") == "kernel.1"


async def test_mark_healthy_detects_pending_update(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> None:
    """Test mark_healthy recovers a pending update and raises a reboot issue."""
    rauc_service: RaucService = all_dbus_services["rauc"]
    rauc_service.response_get_primary = "kernel.0"

    await coresys.os.load()
    with patch.object(
        coresys.dbus.rauc,
        "mark",
        AsyncMock(return_value=["kernel.1", "marked slot kernel.1 as good"]),
    ) as mark:
        await coresys.os.mark_healthy()

    assert coresys.os.version_pending == AwesomeVersion("9.0.dev20220818")
    assert (
        IssueType.REBOOT_REQUIRED,
        ContextType.SYSTEM,
    ) in {(issue.type, issue.context) for issue in coresys.resolution.issues}
    assert (
        SuggestionType.EXECUTE_REBOOT,
        ContextType.SYSTEM,
    ) in {
        (suggestion.type, suggestion.context)
        for suggestion in coresys.resolution.suggestions
    }
    # The pending update must not be cancelled by marking the booted slot active
    mark.assert_called_once_with(RaucState.GOOD, "booted")


async def test_mark_healthy_no_pending_update(coresys: CoreSys) -> None:
    """Test mark_healthy finds no pending update when the primary slot is booted."""
    await coresys.os.load()
    with patch.object(
        coresys.dbus.rauc,
        "mark",
        AsyncMock(return_value=["kernel.1", "marked slot kernel.1 as good"]),
    ):
        await coresys.os.mark_healthy()

    assert coresys.os.version_pending is None
    assert (
        IssueType.REBOOT_REQUIRED,
        ContextType.SYSTEM,
    ) not in {(issue.type, issue.context) for issue in coresys.resolution.issues}


async def test_mark_healthy_stale_primary_before_mark_good(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> None:
    """Test pending update detection runs after the booted slot is marked good.

    rauc's GRUB backend does not treat a slot with boot attempts pending as
    primary. The booted slot has a boot attempt recorded until it is marked
    good, so on every boot GetPrimary reports the previous slot as primary
    until then. Detecting the pending update from that stale response raised
    a bogus reboot issue on every boot on GRUB systems.
    """
    rauc_service: RaucService = all_dbus_services["rauc"]
    rauc_service.response_get_primary = "kernel.0"

    async def mark(state: RaucState, slot_identifier: str) -> list[str]:
        # Marking the booted slot good resets its boot attempt counter,
        # making it eligible as primary again
        rauc_service.response_get_primary = "kernel.1"
        return ["kernel.1", f"marked slot kernel.1 as {state}"]

    await coresys.os.load()
    assert coresys.os.version_pending is None

    with patch.object(coresys.dbus.rauc, "mark", side_effect=mark) as mark_mock:
        await coresys.os.mark_healthy()

    assert coresys.os.version_pending is None
    assert (
        IssueType.REBOOT_REQUIRED,
        ContextType.SYSTEM,
    ) not in {(issue.type, issue.context) for issue in coresys.resolution.issues}
    assert mark_mock.call_args_list == [
        call(RaucState.GOOD, "booted"),
        call(RaucState.ACTIVE, "booted"),
    ]


@pytest.mark.parametrize(
    ("os_available", "expected_service"),
    [
        ("17.3", "hassos-config.service"),
        ("18.0.rc1", "haos-config.service"),
        ("18.0", "haos-config.service"),
    ],
    indirect=["os_available"],
)
async def test_config_sync_service_name(
    coresys: CoreSys, os_available: None, expected_service: str
) -> None:
    """Test config_sync uses the correct service name per OS version."""
    with patch.object(coresys.host.services, "restart", new=AsyncMock()) as restart:
        await coresys.os.config_sync()

    restart.assert_called_once_with(expected_service)
