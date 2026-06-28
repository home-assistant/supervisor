"""Test Raspberry Pi firmware update check."""

from unittest.mock import PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.dbus.agent import OSAgent
from supervisor.resolution.checks.rpi_firmware_update import CheckRpiFirmwareUpdate
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

from tests.dbus_service_mocks.agent_boards_rpi_firmware import (
    RPiFirmware as RPiFirmwareService,
)
from tests.dbus_service_mocks.base import DBusServiceMock


@pytest.fixture(autouse=True)
def fixture_os_agent_version():
    """Mock OS Agent version with Raspberry Pi firmware support."""
    with patch.object(
        OSAgent, "version", new=PropertyMock(return_value=AwesomeVersion("1.9.0"))
    ):
        yield


async def test_check_creates_issue(
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
):
    """Test check creates issue when Raspberry Pi firmware update is available."""
    rpi_service: RPiFirmwareService = os_agent_services["agent_boards_rpi_firmware"]
    await coresys.dbus.agent.board.rpi_firmware.update()
    await coresys.core.set_state(CoreState.RUNNING)

    check = CheckRpiFirmwareUpdate(coresys)
    await check()

    assert (
        Issue(
            IssueType.RPI_FIRMWARE_UPDATE_AVAILABLE,
            ContextType.SYSTEM,
            reference_extra={
                "current_version": "1618412973",
                "latest_version": "1700000000",
            },
        )
        in coresys.resolution.issues
    )
    assert (
        Suggestion(
            SuggestionType.UPDATE_RPI_FIRMWARE,
            ContextType.SYSTEM,
            reference_extra={
                "current_version": "1618412973",
                "latest_version": "1700000000",
            },
        )
        in coresys.resolution.suggestions
    )
    assert rpi_service.update_called is False


async def test_check_cleans_issue_when_update_no_longer_available(
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
):
    """Test check dismisses issue when Raspberry Pi firmware is current."""
    rpi_service: RPiFirmwareService = os_agent_services["agent_boards_rpi_firmware"]
    await coresys.dbus.agent.board.rpi_firmware.update()
    await coresys.core.set_state(CoreState.RUNNING)

    check = CheckRpiFirmwareUpdate(coresys)
    await check()
    assert [
        issue
        for issue in coresys.resolution.issues
        if issue.type == IssueType.RPI_FIRMWARE_UPDATE_AVAILABLE
    ]

    rpi_service.set_state(update_available=False)
    await coresys.dbus.agent.board.rpi_firmware.update()
    await check()

    assert not [
        issue
        for issue in coresys.resolution.issues
        if issue.type == IssueType.RPI_FIRMWARE_UPDATE_AVAILABLE
    ]


async def test_check_replaces_available_issue_with_blocked_issue(
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
):
    """Test check replaces available issue when update becomes blocked."""
    rpi_service: RPiFirmwareService = os_agent_services["agent_boards_rpi_firmware"]
    await coresys.dbus.agent.board.rpi_firmware.update()
    await coresys.core.set_state(CoreState.RUNNING)

    check = CheckRpiFirmwareUpdate(coresys)
    await check()
    assert [
        issue
        for issue in coresys.resolution.issues
        if issue.type == IssueType.RPI_FIRMWARE_UPDATE_AVAILABLE
    ]

    rpi_service.set_state(update_blocked=True, blocked_reason="unsupported_boot_device")
    await coresys.dbus.agent.board.rpi_firmware.update()
    await check()

    assert not [
        issue
        for issue in coresys.resolution.issues
        if issue.type == IssueType.RPI_FIRMWARE_UPDATE_AVAILABLE
    ]
    assert (
        Issue(
            IssueType.RPI_FIRMWARE_UPDATE_BLOCKED,
            ContextType.SYSTEM,
            reference_extra={
                "current_version": "1618412973",
                "latest_version": "1700000000",
                "blocked_reason": "unsupported_boot_device",
            },
        )
        in coresys.resolution.issues
    )


async def test_check_ignored_without_supported_os_agent(
    coresys: CoreSys,
):
    """Test check is ignored when OS Agent does not expose firmware management."""
    await coresys.core.set_state(CoreState.RUNNING)

    with patch.object(
        OSAgent, "version", new=PropertyMock(return_value=AwesomeVersion("1.8.0"))
    ):
        await CheckRpiFirmwareUpdate(coresys)()

    assert not coresys.resolution.issues


async def test_check_creates_reboot_issue_when_update_pending(
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
):
    """Test check creates reboot issue when Raspberry Pi firmware update is pending."""
    rpi_service: RPiFirmwareService = os_agent_services["agent_boards_rpi_firmware"]
    rpi_service.set_state(update_available=False, update_pending=True)
    await coresys.dbus.agent.board.rpi_firmware.update()
    await coresys.core.set_state(CoreState.RUNNING)

    await CheckRpiFirmwareUpdate(coresys)()

    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        in coresys.resolution.issues
    )
    assert (
        Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)
        in coresys.resolution.suggestions
    )
