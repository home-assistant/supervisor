"""Test that we are reading app files correctly."""

import errno
import json
import logging
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from supervisor.const import REPOSITORY_LOCAL, UpdateChannel
from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

from tests.common import load_json_fixture

# pylint: disable=protected-access


async def test_read_app_files(coresys: CoreSys):
    """Test that we are reading app files correctly."""
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
        app_list = await coresys.store.data._find_app_configs(Path("test"), {})

        assert len(app_list) == 1
        assert str(app_list[0]) == "addon/config.yml"


async def test_reading_app_files_error(coresys: CoreSys):
    """Test error trying to read app files."""
    corrupt_repo = Issue(IssueType.CORRUPT_REPOSITORY, ContextType.STORE, "test")
    reset_repo = Suggestion(SuggestionType.EXECUTE_RESET, ContextType.STORE, "test")

    with patch("pathlib.Path.glob", side_effect=(err := OSError())):
        err.errno = errno.EBUSY
        assert (await coresys.store.data._find_app_configs(Path("test"), {})) is None
        assert corrupt_repo in coresys.resolution.issues
        assert reset_repo in coresys.resolution.suggestions
        assert coresys.core.healthy is True

        coresys.resolution.dismiss_issue(
            coresys.resolution.get_issue_if_present(corrupt_repo)
        )
        err.errno = errno.EBADMSG
        assert (await coresys.store.data._find_app_configs(Path("test"), {})) is None
        assert corrupt_repo in coresys.resolution.issues
        assert reset_repo not in coresys.resolution.suggestions
        assert coresys.core.healthy is False


@pytest.mark.parametrize(
    ("repository", "channel", "expect_warning"),
    [
        # A local app's author can act on the advisory.
        (REPOSITORY_LOCAL, UpdateChannel.STABLE, True),
        # A regular user browsing the store cannot; keep it out of their logs.
        ("094b3f00", UpdateChannel.STABLE, False),
        # A developer on the dev channel is testing store apps, so surface it.
        ("094b3f00", UpdateChannel.DEV, True),
    ],
)
async def test_deprecation_advisory_log_level(
    coresys: CoreSys,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    repository: str,
    channel: UpdateChannel,
    expect_warning: bool,
):
    """Deprecation advisories only warn for local apps or on the dev channel."""
    config = load_json_fixture("basic-app-config.json")
    config["advanced"] = True  # Deprecated field, triggers an advisory.
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config), encoding="utf-8")

    coresys.updater.channel = channel

    with (
        patch.object(
            coresys.store.data,
            "_find_app_configs",
            AsyncMock(return_value=[config_file]),
        ),
        caplog.at_level(logging.DEBUG, logger="supervisor.apps.validate"),
    ):
        apps = await coresys.store.data._read_apps_folder(tmp_path, repository)

    assert apps  # Config parsed successfully.
    advisories = [
        record
        for record in caplog.records
        if record.name == "supervisor.apps.validate"
        and "deprecated 'advanced'" in record.getMessage()
    ]
    assert advisories  # The advisory is always emitted at some level.
    assert (
        any(record.levelno >= logging.WARNING for record in advisories)
        is expect_warning
    )
