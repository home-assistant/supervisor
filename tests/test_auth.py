"""Test auth object."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from supervisor.auth import LoginResult
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
    mock_auth_backend.return_value = LoginResult(group_ids=["system-admin"])
    mock_api_state.return_value = True

    assert await coresys.auth.check_login(app, "username", "password")
    assert mock_auth_backend.called


async def test_auth_request_without_backend(coresys, mock_auth_backend, mock_api_state):
    """Make simple auth without request."""

    app = MagicMock()
    mock_auth_backend.return_value = LoginResult(group_ids=["system-admin"])
    mock_api_state.return_value = False

    assert not await coresys.auth.check_login(app, "username", "password")
    assert not mock_auth_backend.called


async def test_auth_request_without_backend_cache(
    coresys, mock_auth_backend, mock_api_state
):
    """Make simple auth without request."""

    app = MagicMock()
    mock_auth_backend.return_value = LoginResult(group_ids=["system-admin"])
    mock_api_state.return_value = False

    await coresys.auth._update_cache("username", "password", ["system-admin"])

    assert await coresys.auth.check_login(app, "username", "password")
    assert not mock_auth_backend.called


async def test_auth_request_with_backend_cache_update(
    coresys, mock_auth_backend, mock_api_state
):
    """Make simple auth without request and cache update."""

    app = MagicMock()
    mock_auth_backend.return_value = None
    mock_api_state.return_value = True

    await coresys.auth._update_cache("username", "password", ["system-admin"])

    assert await coresys.auth.check_login(app, "username", "password")

    await asyncio.sleep(0)

    assert mock_auth_backend.called
    await coresys.auth._dismatch_cache("username", "password")
    assert not await coresys.auth.check_login(app, "username", "password")


@pytest.mark.parametrize(
    "backend_result",
    [
        pytest.param(LoginResult(group_ids=["system-users"]), id="new_password"),
        pytest.param(None, id="wrong_password"),
    ],
)
async def test_auth_request_cache_mismatch_checks_backend(
    coresys: CoreSys,
    mock_auth_backend: AsyncMock,
    mock_api_state: AsyncMock,
    backend_result: LoginResult | None,
):
    """Test a cached user with a different password is validated by Core."""
    app = MagicMock()
    mock_auth_backend.return_value = backend_result
    mock_api_state.return_value = True

    await coresys.auth._update_cache("username", "old_password", ["system-admin"])

    assert (
        await coresys.auth.check_login(app, "username", "new_password")
        == backend_result
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

    await coresys.auth._update_cache("username", "password", ["system-admin"])

    with patch.object(coresys.homeassistant.api, "make_request", make_request):
        assert await coresys.auth.check_login(app, "username", "password")
        task = coresys.auth._running["username"]

        assert not await coresys.auth.check_login(app, "username", "wrong")
        assert coresys.auth._running["username"] is task

        await asyncio.wait_for(task, 1)

    assert "username" not in coresys.auth._running
    assert make_request.call_count == 2
    assert coresys.auth._check_cache("username", "password") is None


async def test_auth_background_refresh_cancelled_before_start(
    coresys: CoreSys, mock_auth_backend: AsyncMock, mock_api_state: AsyncMock
):
    """Test a background refresh cancelled before it runs is not left tracked."""
    app = MagicMock()
    mock_api_state.return_value = True

    await coresys.auth._update_cache("username", "password", ["system-admin"])

    assert await coresys.auth.check_login(app, "username", "password")
    task = coresys.auth._running["username"]
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert "username" not in coresys.auth._running
    mock_auth_backend.assert_not_awaited()


async def test_auth_cached_groups_returned_without_backend(
    coresys: CoreSys, mock_auth_backend: AsyncMock, mock_api_state: AsyncMock
):
    """Test the cached group IDs are returned while Core is unavailable."""
    app = MagicMock()
    mock_api_state.return_value = False

    await coresys.auth._update_cache("username", "password", ["system-admin"])

    assert await coresys.auth.check_login(app, "username", "password") == LoginResult(
        group_ids=["system-admin"]
    )
    mock_auth_backend.assert_not_awaited()


async def test_auth_legacy_cache_entry_has_no_groups(
    coresys: CoreSys, mock_auth_backend: AsyncMock, mock_api_state: AsyncMock
):
    """Test a cache entry written before group IDs were cached still validates."""
    app = MagicMock()
    mock_api_state.return_value = False
    coresys.auth._data[coresys.auth._rehash("username")] = coresys.auth._rehash(
        "password", "username"
    )

    assert await coresys.auth.check_login(app, "username", "password") == LoginResult(
        group_ids=[]
    )
    assert await coresys.auth.check_login(app, "username", "wrong") is None


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        pytest.param('{"group_ids": ["system-admin"]}', ["system-admin"], id="groups"),
        pytest.param("", [], id="empty_body_from_older_core"),
        pytest.param("{}", [], id="no_groups_field"),
        pytest.param('{"group_ids": "system-admin"}', [], id="not_a_list"),
        pytest.param(
            '{"group_ids": ["system-admin", 1]}', ["system-admin"], id="mixed"
        ),
    ],
)
async def test_auth_backend_login_group_ids(
    coresys: CoreSys, mock_api_state: AsyncMock, body: str, expected: list[str]
):
    """Test the group IDs Core reports are returned and cached."""
    del coresys.auth._backend_login
    app = MagicMock()
    mock_api_state.return_value = True
    make_request = MagicMock(return_value=MockResponse(status=200, text=body))

    with patch.object(coresys.homeassistant.api, "make_request", make_request):
        assert await coresys.auth.check_login(
            app, "username", "password"
        ) == LoginResult(group_ids=expected)

    assert coresys.auth._cached_login("username") == LoginResult(group_ids=expected)
