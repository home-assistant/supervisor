"""Test system fixup adopt data disk."""

from dbus_fast import DBusError, ErrorType, Variant
import pytest

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.system_adopt_data_disk import FixupSystemAdoptDataDisk

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.logind import Logind as LogindService
from tests.dbus_service_mocks.udisks2_filesystem import Filesystem as FilesystemService
from tests.dbus_service_mocks.udisks2_manager import (
    UDisks2Manager as UDisks2ManagerService,
)


@pytest.fixture(name="sda1_filesystem_service")
async def fixture_sda1_filesystem_service(
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> FilesystemService:
    """Return sda1 filesystem service."""
    return udisks2_services["udisks2_filesystem"][
        "/org/freedesktop/UDisks2/block_devices/sda1"
    ]


@pytest.fixture(name="mmcblk1p3_filesystem_service")
async def fixture_mmcblk1p3_filesystem_service(
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> FilesystemService:
    """Return mmcblk1p3 filesystem service."""
    return udisks2_services["udisks2_filesystem"][
        "/org/freedesktop/UDisks2/block_devices/mmcblk1p3"
    ]


@pytest.fixture(name="udisks2_service")
async def fixture_udisks2_service(
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> UDisks2ManagerService:
    """Return udisks2 manager service."""
    return udisks2_services["udisks2_manager"]


@pytest.fixture(name="logind_service")
async def fixture_logind_service(
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> LogindService:
    """Return logind service."""
    return all_dbus_services["logind"]


async def test_fixup(
    coresys: CoreSys,
    mmcblk1p3_filesystem_service: FilesystemService,
    udisks2_service: UDisks2ManagerService,
    logind_service: LogindService,
):
    """Test fixup."""
    mmcblk1p3_filesystem_service.SetLabel.calls.clear()
    logind_service.Reboot.calls.clear()
    system_adopt_data_disk = FixupSystemAdoptDataDisk(coresys)

    assert not system_adopt_data_disk.auto

    coresys.resolution.suggestions = Suggestion(
        SuggestionType.ADOPT_DATA_DISK, ContextType.SYSTEM, reference="/dev/sda1"
    )
    coresys.resolution.issues = Issue(
        IssueType.MULTIPLE_DATA_DISKS, ContextType.SYSTEM, reference="/dev/sda1"
    )
    udisks2_service.resolved_devices = [
        "/org/freedesktop/UDisks2/block_devices/mmcblk1p3"
    ]

    await system_adopt_data_disk()

    assert mmcblk1p3_filesystem_service.SetLabel.calls == [
        ("hassos-data-old", {"auth.no_user_interaction": Variant("b", True)})
    ]
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0
    assert logind_service.Reboot.calls == [(False,)]


async def test_fixup_device_removed(
    coresys: CoreSys,
    mmcblk1p3_filesystem_service: FilesystemService,
    udisks2_service: UDisks2ManagerService,
    logind_service: LogindService,
    caplog: pytest.LogCaptureFixture,
):
    """Test fixup when device removed."""
    mmcblk1p3_filesystem_service.SetLabel.calls.clear()
    logind_service.Reboot.calls.clear()
    system_adopt_data_disk = FixupSystemAdoptDataDisk(coresys)

    assert not system_adopt_data_disk.auto

    coresys.resolution.suggestions = Suggestion(
        SuggestionType.ADOPT_DATA_DISK, ContextType.SYSTEM, reference="/dev/sda1"
    )
    coresys.resolution.issues = Issue(
        IssueType.MULTIPLE_DATA_DISKS, ContextType.SYSTEM, reference="/dev/sda1"
    )

    udisks2_service.resolved_devices = []
    await system_adopt_data_disk()

    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0
    assert "Data disk at /dev/sda1 with name conflict was removed" in caplog.text
    assert mmcblk1p3_filesystem_service.SetLabel.calls == []
    assert logind_service.Reboot.calls == []


async def test_fixup_reboot_failed(
    coresys: CoreSys,
    mmcblk1p3_filesystem_service: FilesystemService,
    udisks2_service: UDisks2ManagerService,
    logind_service: LogindService,
    caplog: pytest.LogCaptureFixture,
):
    """Test fixup when reboot fails."""
    mmcblk1p3_filesystem_service.SetLabel.calls.clear()
    logind_service.side_effect_reboot = DBusError(ErrorType.SERVICE_ERROR, "error")
    system_adopt_data_disk = FixupSystemAdoptDataDisk(coresys)

    assert not system_adopt_data_disk.auto

    coresys.resolution.suggestions = Suggestion(
        SuggestionType.ADOPT_DATA_DISK, ContextType.SYSTEM, reference="/dev/sda1"
    )
    coresys.resolution.issues = Issue(
        IssueType.MULTIPLE_DATA_DISKS, ContextType.SYSTEM, reference="/dev/sda1"
    )
    udisks2_service.resolved_devices = [
        "/org/freedesktop/UDisks2/block_devices/mmcblk1p3"
    ]

    await system_adopt_data_disk()

    assert mmcblk1p3_filesystem_service.SetLabel.calls == [
        ("hassos-data-old", {"auth.no_user_interaction": Variant("b", True)})
    ]
    assert len(coresys.resolution.suggestions) == 1
    assert (
        Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)
        in coresys.resolution.suggestions
    )
    assert len(coresys.resolution.issues) == 1
    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        in coresys.resolution.issues
    )
    assert "Could not reboot host to finish data disk adoption" in caplog.text
