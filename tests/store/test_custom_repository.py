"""Test add custom repository."""
import json
from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_add_valid_repository(coresys, store_manager):
    """Test add custom repository."""
    current = coresys.config.addons_repositories
    with patch("supervisor.store.repository.Repository.load", return_value=True), patch(
        "pathlib.Path.read_text",
        return_value=json.dumps({"name": "Awesome repository"}),
    ):
        await store_manager.update_repositories(current + ["http://example.com"])
    assert "http://example.com" in coresys.config.addons_repositories


@pytest.mark.asyncio
async def test_add_invalid_repository(coresys, store_manager):
    """Test add custom repository."""
    current = coresys.config.addons_repositories
    with patch("supervisor.store.repository.Repository.load", return_value=True), patch(
        "pathlib.Path.read_text",
        return_value="",
    ):
        await store_manager.update_repositories(current + ["http://example.com"])
    assert "http://example.com" not in coresys.config.addons_repositories
