"""Test schema validation."""

import pytest
from voluptuous import Invalid

from supervisor.store.validate import repositories


@pytest.mark.parametrize(
    ("repo_list", "valid"),
    [
        (["core", "local"], True),
        (["https://github.com/hassio-addons/repository"], True),
        (["https://github.com/hassio-addons/repository#beta"], True),
        (["https://github.com/hassio-addons/repository#feature/hot-new-stuff"], True),
        (["not_a_url"], False),
        (
            ["https://github.com/hassio-addons/repository #beta"],
            False,
        ),
        (["https://fail.com/duplicate", "https://fail.com/duplicate"], False),
    ],
)
async def test_repository_validate(repo_list: list[str], valid: bool):
    """Test repository list validate."""
    if valid:
        assert repositories(repo_list) == repo_list
    else:
        with pytest.raises(Invalid):
            repositories(repo_list)


@pytest.mark.parametrize(
    ("repo_list", "expected"),
    [
        (
            [" \t\nhttps://github.com/hassio-addons/repository \n\t"],
            ["https://github.com/hassio-addons/repository"],
        ),
    ],
)
async def test_repository_validate_strips_whitespace(
    repo_list: list[str], expected: list[str]
):
    """Test repository validation strips leading/trailing whitespace."""
    assert repositories(repo_list) == expected
