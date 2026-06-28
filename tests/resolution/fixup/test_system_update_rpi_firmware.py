"""Test update Raspberry Pi firmware fixup."""

from unittest.mock import AsyncMock

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.system_update_rpi_firmware import (
    FixupSystemUpdateRpiFirmware,
)


async def test_fixup(coresys: CoreSys):
    """Test fixup."""
    update_rpi_firmware = FixupSystemUpdateRpiFirmware(coresys)

    assert update_rpi_firmware.auto is False

    coresys.resolution.add_suggestion(
        Suggestion(SuggestionType.UPDATE_RPI_FIRMWARE, ContextType.SYSTEM)
    )
    coresys.resolution.add_issue(
        Issue(IssueType.RPI_FIRMWARE_UPDATE_AVAILABLE, ContextType.SYSTEM)
    )

    mock_update = AsyncMock()
    coresys.os.update_raspberrypi_firmware = mock_update

    await update_rpi_firmware()

    mock_update.assert_called_once()
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0
