"""Test Home Assistant OS functionality."""

from unittest.mock import AsyncMock, PropertyMock, patch

from awesomeversion import AwesomeVersion
from dbus_fast import Variant
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import HassOSJobError

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
