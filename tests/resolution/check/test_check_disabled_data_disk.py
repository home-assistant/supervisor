"""Test check for disabled data disk."""

# pylint: disable=import-error
from dataclasses import replace
from unittest.mock import patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.disabled_data_disk import CheckDisabledDataDisk
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.udisks2_block import Block as BlockService


@pytest.fixture(name="sda1_block_service")
async def fixture_sda1_block_service(
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> BlockService:
    """Return sda1 block service."""
    yield udisks2_services["udisks2_block"][
        "/org/freedesktop/UDisks2/block_devices/sda1"
    ]


async def test_base(coresys: CoreSys):
    """Test check basics."""
    disabled_data_disk = CheckDisabledDataDisk(coresys)
    assert disabled_data_disk.slug == "disabled_data_disk"
    assert disabled_data_disk.enabled


async def test_check(coresys: CoreSys, sda1_block_service: BlockService):
    """Test check."""
    disabled_data_disk = CheckDisabledDataDisk(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    await disabled_data_disk.run_check()

    assert len(coresys.resolution.issues) == 0
    assert len(coresys.resolution.suggestions) == 0

    sda1_block_service.emit_properties_changed({"IdLabel": "hassos-data-dis"})
    await sda1_block_service.ping()

    await disabled_data_disk.run_check()

    assert coresys.resolution.issues == [
        Issue(IssueType.DISABLED_DATA_DISK, ContextType.SYSTEM, reference="/dev/sda1")
    ]
    assert coresys.resolution.suggestions == [
        Suggestion(
            SuggestionType.RENAME_DATA_DISK, ContextType.SYSTEM, reference="/dev/sda1"
        ),
        Suggestion(
            SuggestionType.ADOPT_DATA_DISK, ContextType.SYSTEM, reference="/dev/sda1"
        ),
    ]


async def test_approve(coresys: CoreSys, sda1_block_service: BlockService):
    """Test approve."""
    disabled_data_disk = CheckDisabledDataDisk(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    assert not await disabled_data_disk.approve_check(reference="/dev/sda1")

    sda1_block_service.fixture = replace(
        sda1_block_service.fixture, IdLabel="hassos-data-dis"
    )

    assert await disabled_data_disk.approve_check(reference="/dev/sda1")


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    disabled_data_disk = CheckDisabledDataDisk(coresys)
    should_run = disabled_data_disk.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.disabled_data_disk.CheckDisabledDataDisk.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await disabled_data_disk()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await disabled_data_disk()
            check.assert_not_called()
            check.reset_mock()
