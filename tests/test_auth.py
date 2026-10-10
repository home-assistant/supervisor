"""Test auth object."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from supervisor.coresys import CoreSys

from tests.common import MockResponse

# pylint: disable=protected-access


@pytest.fixture(name="mock_auth_backend", autouse=True)
def mock_auth_backend_fixture(coresys):
    """Fix auth backend request."""
    mock_auth_backend = AsyncMock()
    coresys.auth._backend_login = mock_auth_backend

    return mock_auth_backend


@pytest.fixture(name="mock_api_state", autouse=True)
def mock_api_state_fixture(coresys):
    """Fix auth backend request."""
    mock_api_state = AsyncMock()
    coresys.homeassistant.api.check_api_state = mock_api_state

    return mock_api_state


async def test_auth_request_with_backend(coresys, mock_auth_backend, mock_api_state):
    """Make simple auth request."""

    app = MagicMock()
    mock_auth_backend.return_value = True
    mock_api_state.return_value = True

    assert await coresys.auth.check_login(app, "username", "password")
    assert mock_auth_backend.called


async def test_auth_request_without_backend(coresys, mock_auth_backend, mock_api_state):
    """Make simple auth without request."""

    app = MagicMock()
    mock_auth_backend.return_value = True
    mock_api_state.return_value = False

    assert not await coresys.auth.check_login(app, "username", "password")
    assert not mock_auth_backend.called


async def test_auth_request_without_backend_cache(
    coresys, mock_auth_backend, mock_api_state
):
    """Make simple auth without request."""

    app = MagicMock()
    mock_auth_backend.return_value = True
    mock_api_state.return_value = False

    await coresys.auth._update_cache("username", "password")

    assert await coresys.auth.check_login(app, "username", "password")
    assert not mock_auth_backend.called


async def test_auth_request_with_backend_cache_update(
    coresys, mock_auth_backend, mock_api_state
):
    """Make simple auth without request and cache update."""

    app = MagicMock()
    mock_auth_backend.return_value = False
    mock_api_state.return_value = True

    await coresys.auth._update_cache("username", "password")

    assert await coresys.auth.check_login(app, "username", "password")

    await asyncio.sleep(0)

    assert mock_auth_backend.called
    await coresys.auth._dismatch_cache("username", "password")
    assert not await coresys.auth.check_login(app, "username", "password")


@pytest.mark.parametrize(
    "backend_result",
    [pytest.param(True, id="new_password"), pytest.param(False, id="wrong_password")],
)
async def test_auth_request_cache_mismatch_checks_backend(
    coresys: CoreSys,
    mock_auth_backend: AsyncMock,
    mock_api_state: AsyncMock,
    backend_result: bool,
):
    """Test a cached user with a different password is validated by Core."""
    app = MagicMock()
    mock_auth_backend.return_value = backend_result
    mock_api_state.return_value = True

    await coresys.auth._update_cache("username", "old_password")

    assert await coresys.auth.check_login(app, "username", "new_password") is (
        backend_result
    )
    mock_auth_backend.assert_awaited_once_with(app, "username", "new_password")
    assert "username" not in coresys.auth._running


async def test_auth_foreground_login_keeps_background_refresh(
    coresys: CoreSys, mock_api_state: AsyncMock
):
    """Test a foreground login does not drop a pending background refresh."""
    # Exercise the real backend login instead of the autouse mock
    del coresys.auth._backend_login
    app = MagicMock()
    mock_api_state.return_value = True
    make_request = MagicMock(return_value=MockResponse(status=401))

    await coresys.auth._update_cache("username", "password")

    with patch.object(coresys.homeassistant.api, "make_request", make_request):
        assert await coresys.auth.check_login(app, "username", "password")
        task = coresys.auth._running["username"]

        assert not await coresys.auth.check_login(app, "username", "wrong")
        assert coresys.auth._running["username"] is task

        await asyncio.wait_for(task, 1)

    assert "username" not in coresys.auth._running
    assert make_request.call_count == 2
    assert coresys.auth._check_cache("username", "password") is None
