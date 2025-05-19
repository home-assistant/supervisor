"""Test that we are reading add-on files correctly."""

import errno
from pathlib import Path
from unittest.mock import patch

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

# pylint: disable=protected-access


async def test_read_addon_files(coresys: CoreSys):
    """Test that we are reading add-on files correctly."""
    with patch(
        "pathlib.Path.glob",
        return_value=[
            Path("addon/config.yml"),
            Path(".git/config.yml"),
            Path("somepath/.git/config.yml"),
            Path("somepath/deeper_in_the_structure/.github/config.yml"),
            Path(".github/config.yml"),
            Path("some/rootfs/config.yml"),
            Path(".circleci/config.yml"),
        ],
    ):
        addon_list = await coresys.store.data._find_addon_configs(Path("test"), {})

        assert len(addon_list) == 1
        assert str(addon_list[0]) == "addon/config.yml"


async def test_reading_addon_files_error(coresys: CoreSys):
    """Test error trying to read addon files."""
    corrupt_repo = Issue(IssueType.CORRUPT_REPOSITORY, ContextType.STORE, "test")
    reset_repo = Suggestion(SuggestionType.EXECUTE_RESET, ContextType.STORE, "test")

    with patch("pathlib.Path.glob", side_effect=(err := OSError())):
        err.errno = errno.EBUSY
        assert (await coresys.store.data._find_addon_configs(Path("test"), {})) is None
        assert corrupt_repo in coresys.resolution.issues
        assert reset_repo in coresys.resolution.suggestions
        assert coresys.core.healthy is True

        coresys.resolution.dismiss_issue(corrupt_repo)
        err.errno = errno.EBADMSG
        assert (await coresys.store.data._find_addon_configs(Path("test"), {})) is None
        assert corrupt_repo in coresys.resolution.issues
        assert reset_repo not in coresys.resolution.suggestions
        assert coresys.core.healthy is False
