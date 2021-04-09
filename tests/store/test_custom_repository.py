"""Test add custom repository."""
import json
from unittest.mock import patch

import pytest

from supervisor.resolution.const import SuggestionType
from supervisor.store import BUILTIN_REPOSITORIES


@pytest.mark.asyncio
async def test_add_valid_repository(coresys, store_manager):
    """Test add custom repository."""
    current = coresys.config.addons_repositories
    with patch("supervisor.store.repository.Repository.load", return_value=None), patch(
        "supervisor.utils.common.read_yaml_file",
        return_value={"name": "Awesome repository"},
    ), patch("pathlib.Path.exists", return_value=True):

        await store_manager.update_repositories(current + ["http://example.com"])
        assert store_manager.get_from_url("http://example.com").validate()
    assert "http://example.com" in coresys.config.addons_repositories


@pytest.mark.asyncio
async def test_add_valid_repository_url(coresys, store_manager):
    """Test add custom repository."""
    current = coresys.config.addons_repositories
    with patch("supervisor.store.repository.Repository.load", return_value=None), patch(
        "supervisor.utils.common.read_yaml_file",
        return_value={"name": "Awesome repository"},
    ), patch("pathlib.Path.exists", return_value=True):
        await store_manager.update_repositories(current + ["http://example.com"])
        assert store_manager.get_from_url("http://example.com").validate()
    assert "http://example.com" in coresys.config.addons_repositories


@pytest.mark.asyncio
async def test_add_invalid_repository(coresys, store_manager):
    """Test add custom repository."""
    current = coresys.config.addons_repositories
    with patch("supervisor.store.repository.Repository.load", return_value=None), patch(
        "pathlib.Path.read_text",
        return_value="",
    ):
        await store_manager.update_repositories(current + ["http://example.com"])
        assert not store_manager.get_from_url("http://example.com").validate()

    assert "http://example.com" in coresys.config.addons_repositories
    assert coresys.resolution.suggestions[-1].type == SuggestionType.EXECUTE_REMOVE


@pytest.mark.asyncio
async def test_add_invalid_repository_file(coresys, store_manager):
    """Test add custom repository."""
    current = coresys.config.addons_repositories
    with patch("supervisor.store.repository.Repository.load", return_value=None), patch(
        "pathlib.Path.read_text",
        return_value=json.dumps({"name": "Awesome repository"}),
    ), patch("pathlib.Path.exists", return_value=False):
        await store_manager.update_repositories(current + ["http://example.com"])
        assert not store_manager.get_from_url("http://example.com").validate()

    assert "http://example.com" in coresys.config.addons_repositories
    assert coresys.resolution.suggestions[-1].type == SuggestionType.EXECUTE_REMOVE


@pytest.mark.asyncio
async def test_preinstall_valid_repository(coresys, store_manager):
    """Test add core repository valid."""
    with patch("supervisor.store.repository.Repository.load", return_value=None):
        await store_manager.update_repositories(BUILTIN_REPOSITORIES)
        assert store_manager.get("core").validate()
        assert store_manager.get("local").validate()
