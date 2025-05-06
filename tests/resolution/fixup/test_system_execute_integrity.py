"""Test evaluation base."""

# pylint: disable=import-error,protected-access
from datetime import timedelta
from unittest.mock import AsyncMock

import time_machine

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.system_execute_integrity import (
    FixupSystemExecuteIntegrity,
)
from supervisor.security.const import ContentTrustResult, IntegrityResult
from supervisor.utils.dt import utcnow


async def test_fixup(coresys: CoreSys, supervisor_internet: AsyncMock):
    """Test fixup."""
    system_execute_integrity = FixupSystemExecuteIntegrity(coresys)

    assert system_execute_integrity.auto

    coresys.resolution.add_suggestion(
        Suggestion(SuggestionType.EXECUTE_INTEGRITY, ContextType.SYSTEM)
    )
    coresys.resolution.add_issue(Issue(IssueType.TRUST, ContextType.SYSTEM))

    coresys.security.integrity_check = AsyncMock(
        return_value=IntegrityResult(
            ContentTrustResult.PASS,
            ContentTrustResult.PASS,
            {"audio": ContentTrustResult.PASS},
        )
    )

    await system_execute_integrity()

    assert coresys.security.integrity_check.called
    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0


async def test_fixup_error(coresys: CoreSys, supervisor_internet: AsyncMock):
    """Test fixup."""
    system_execute_integrity = FixupSystemExecuteIntegrity(coresys)

    assert system_execute_integrity.auto

    coresys.resolution.add_suggestion(
        Suggestion(SuggestionType.EXECUTE_INTEGRITY, ContextType.SYSTEM)
    )
    coresys.resolution.add_issue(Issue(IssueType.TRUST, ContextType.SYSTEM))

    coresys.security.integrity_check = AsyncMock(
        return_value=IntegrityResult(
            ContentTrustResult.FAILED,
            ContentTrustResult.PASS,
            {"audio": ContentTrustResult.PASS},
        )
    )

    with time_machine.travel(utcnow() + timedelta(hours=24)):
        await system_execute_integrity()

    assert coresys.security.integrity_check.called
    assert len(coresys.resolution.suggestions) == 1
    assert len(coresys.resolution.issues) == 1
