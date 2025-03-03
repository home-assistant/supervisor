"""Test check for multiple data disks."""

# pylint: disable=import-error
from dataclasses import replace
from unittest.mock import patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.multiple_data_disks import CheckMultipleDataDisks
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
    multiple_data_disks = CheckMultipleDataDisks(coresys)
    assert multiple_data_disks.slug == "multiple_data_disks"
    assert multiple_data_disks.enabled


async def test_check(coresys: CoreSys, sda1_block_service: BlockService):
    """Test check."""
    multiple_data_disks = CheckMultipleDataDisks(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    await multiple_data_disks.run_check()

    assert len(coresys.resolution.issues) == 0
    assert len(coresys.resolution.suggestions) == 0

    sda1_block_service.emit_properties_changed({"IdLabel": "hassos-data"})
    await sda1_block_service.ping()

    await multiple_data_disks.run_check()

    assert coresys.resolution.issues == [
        Issue(IssueType.MULTIPLE_DATA_DISKS, ContextType.SYSTEM, reference="/dev/sda1")
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
    multiple_data_disks = CheckMultipleDataDisks(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    assert not await multiple_data_disks.approve_check(reference="/dev/sda1")

    sda1_block_service.fixture = replace(
        sda1_block_service.fixture, IdLabel="hassos-data"
    )

    assert await multiple_data_disks.approve_check(reference="/dev/sda1")


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    multiple_data_disks = CheckMultipleDataDisks(coresys)
    should_run = multiple_data_disks.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.multiple_data_disks.CheckMultipleDataDisks.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await multiple_data_disks()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await multiple_data_disks()
            check.assert_not_called()
            check.reset_mock()
