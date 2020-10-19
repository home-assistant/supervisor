"""Test auth object."""
import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

# pylint: disable=protected-access


@pytest.fixture(name="mock_auth_backend", autouse=True)
def mock_auth_backend_fixture(coresys):
    """Fix auth backend request."""
    mock_auth_backend = AsyncMock()
    coresys.auth._backend_login = mock_auth_backend

    yield mock_auth_backend


@pytest.fixture(name="mock_api_state", autouse=True)
def mock_api_state_fixture(coresys):
    """Fix auth backend request."""
    mock_api_state = AsyncMock()
    coresys.homeassistant.api.check_api_state = mock_api_state

    yield mock_api_state


@pytest.mark.asyncio
async def test_auth_request_with_backend(coresys, mock_auth_backend, mock_api_state):
    """Make simple auth request."""

    addon = MagicMock()
    mock_auth_backend.return_value = True
    mock_api_state.return_value = True

    assert await coresys.auth.check_login(addon, "username", "password")
    assert mock_auth_backend.called


@pytest.mark.asyncio
async def test_auth_request_without_backend(coresys, mock_auth_backend, mock_api_state):
    """Make simple auth without request."""

    addon = MagicMock()
    mock_auth_backend.return_value = True
    mock_api_state.return_value = False

    assert not await coresys.auth.check_login(addon, "username", "password")
    assert not mock_auth_backend.called


@pytest.mark.asyncio
async def test_auth_request_without_backend_cache(
    coresys, mock_auth_backend, mock_api_state
):
    """Make simple auth without request."""

    addon = MagicMock()
    mock_auth_backend.return_value = True
    mock_api_state.return_value = False

    coresys.auth._update_cache("username", "password")

    assert await coresys.auth.check_login(addon, "username", "password")
    assert not mock_auth_backend.called


@pytest.mark.asyncio
async def test_auth_request_with_backend_cache_update(
    coresys, mock_auth_backend, mock_api_state
):
    """Make simple auth without request and cache update."""

    addon = MagicMock()
    mock_auth_backend.return_value = False
    mock_api_state.return_value = True

    coresys.auth._update_cache("username", "password")

    assert await coresys.auth.check_login(addon, "username", "password")

    await asyncio.sleep(0)

    assert mock_auth_backend.called
    coresys.auth._dismatch_cache("username", "password")
    assert not await coresys.auth.check_login(addon, "username", "password")
