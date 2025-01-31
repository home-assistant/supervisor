"""Test schema validation."""

import pytest
from voluptuous import Invalid

from supervisor.store.validate import repositories


@pytest.mark.parametrize(
    "repo_list,valid",
    [
        (["core", "local"], True),
        (["https://github.com/hassio-addons/repository"], True),
        (["not_a_url"], False),
        (["https://fail.com/duplicate", "https://fail.com/duplicate"], False),
    ],
)
async def test_repository_validate(repo_list: list[str], valid: bool):
    """Test repository list validate."""
    if valid:
        processed = repositories(repo_list)
        assert len(processed) == len(repo_list)
        assert set(repositories(repo_list)) == set(repo_list)
    else:
        with pytest.raises(Invalid):
            repositories(repo_list)
