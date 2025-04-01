"""Test system fixup rename data disk."""

# pylint: disable=import-error
from dbus_fast import Variant
import pytest

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.system_rename_data_disk import (
    FixupSystemRenameDataDisk,
)

from tests.dbus_service_mocks.base import DBusServiceMock
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


@pytest.fixture(name="udisks2_service")
async def fixture_udisks2_service(
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> UDisks2ManagerService:
    """Return udisks2 manager service."""
    return udisks2_services["udisks2_manager"]


async def test_fixup(coresys: CoreSys, sda1_filesystem_service: FilesystemService):
    """Test fixup."""
    sda1_filesystem_service.SetLabel.calls.clear()
    system_rename_data_disk = FixupSystemRenameDataDisk(coresys)

    assert not system_rename_data_disk.auto

    coresys.resolution.add_suggestion(
        Suggestion(
            SuggestionType.RENAME_DATA_DISK, ContextType.SYSTEM, reference="/dev/sda1"
        )
    )
    coresys.resolution.add_issue(
        Issue(IssueType.MULTIPLE_DATA_DISKS, ContextType.SYSTEM, reference="/dev/sda1")
    )

    await system_rename_data_disk()

    assert sda1_filesystem_service.SetLabel.calls == [
        (
            "/org/freedesktop/UDisks2/block_devices/sda1",
            "hassos-data-old",
            {"auth.no_user_interaction": Variant("b", True)},
        )
    ]
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0


async def test_fixup_device_removed(
    coresys: CoreSys,
    udisks2_service: UDisks2ManagerService,
    caplog: pytest.LogCaptureFixture,
):
    """Test fixup when device removed."""
    system_rename_data_disk = FixupSystemRenameDataDisk(coresys)

    assert not system_rename_data_disk.auto

    coresys.resolution.add_suggestion(
        Suggestion(
            SuggestionType.RENAME_DATA_DISK, ContextType.SYSTEM, reference="/dev/sda1"
        )
    )
    coresys.resolution.add_issue(
        Issue(IssueType.MULTIPLE_DATA_DISKS, ContextType.SYSTEM, reference="/dev/sda1")
    )

    udisks2_service.resolved_devices = []
    await system_rename_data_disk()

    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0
    assert "Data disk at /dev/sda1 with name conflict was removed" in caplog.text


async def test_fixup_device_not_filesystem(
    coresys: CoreSys,
    udisks2_service: UDisks2ManagerService,
    caplog: pytest.LogCaptureFixture,
):
    """Test fixup when device is no longer a filesystem."""
    system_rename_data_disk = FixupSystemRenameDataDisk(coresys)

    assert not system_rename_data_disk.auto

    coresys.resolution.add_suggestion(
        Suggestion(
            SuggestionType.RENAME_DATA_DISK, ContextType.SYSTEM, reference="/dev/sda1"
        )
    )
    coresys.resolution.add_issue(
        Issue(IssueType.MULTIPLE_DATA_DISKS, ContextType.SYSTEM, reference="/dev/sda1")
    )

    udisks2_service.resolved_devices = ["/org/freedesktop/UDisks2/block_devices/sda"]
    await system_rename_data_disk()

    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0
    assert "Data disk at /dev/sda1 no longer appears to be a filesystem" in caplog.text
