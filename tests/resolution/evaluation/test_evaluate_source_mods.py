"""Test evaluation base."""

# pylint: disable=import-error,protected-access
import errno
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import CodeNotaryError, CodeNotaryUntrusted
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue
from supervisor.resolution.evaluations.source_mods import EvaluateSourceMods


async def test_evaluation(coresys: CoreSys):
    """Test evaluation."""
    with patch(
        "supervisor.resolution.evaluations.source_mods._SUPERVISOR_SOURCE",
        Path(f"{os.getcwd()}/supervisor"),
    ):
        sourcemods = EvaluateSourceMods(coresys)
        await coresys.core.set_state(CoreState.RUNNING)

        assert sourcemods.reason not in coresys.resolution.unsupported
        coresys.security.verify_own_content = AsyncMock(side_effect=CodeNotaryUntrusted)
        await sourcemods()
        assert sourcemods.reason in coresys.resolution.unsupported

        coresys.security.verify_own_content = AsyncMock(side_effect=CodeNotaryError)
        await sourcemods()
        assert sourcemods.reason not in coresys.resolution.unsupported

        coresys.security.verify_own_content = AsyncMock()
        await sourcemods()
        assert sourcemods.reason not in coresys.resolution.unsupported


async def test_did_run(coresys: CoreSys):
    """Test that the evaluation ran as expected."""
    sourcemods = EvaluateSourceMods(coresys)
    should_run = sourcemods.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.evaluations.source_mods.EvaluateSourceMods.evaluate",
        return_value=None,
    ) as evaluate:
        for state in should_run:
            await coresys.core.set_state(state)
            await sourcemods()
            evaluate.assert_called_once()
            evaluate.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await sourcemods()
            evaluate.assert_not_called()
            evaluate.reset_mock()


async def test_evaluation_error(coresys: CoreSys):
    """Test error reading file during evaluation."""
    sourcemods = EvaluateSourceMods(coresys)
    await coresys.core.set_state(CoreState.RUNNING)
    corrupt_fs = Issue(IssueType.CORRUPT_FILESYSTEM, ContextType.SYSTEM)

    assert sourcemods.reason not in coresys.resolution.unsupported
    assert corrupt_fs not in coresys.resolution.issues

    with patch(
        "supervisor.utils.codenotary.dirhash",
        side_effect=(err := OSError()),
    ):
        err.errno = errno.EBUSY
        await sourcemods()
        assert sourcemods.reason not in coresys.resolution.unsupported
        assert corrupt_fs in coresys.resolution.issues
        assert coresys.core.healthy is True

        coresys.resolution.dismiss_issue(corrupt_fs)
        err.errno = errno.EBADMSG
        await sourcemods()
        assert sourcemods.reason not in coresys.resolution.unsupported
        assert corrupt_fs in coresys.resolution.issues
        assert coresys.core.healthy is False
