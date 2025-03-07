"""Test check."""

# pylint: disable=import-error,protected-access
from unittest.mock import AsyncMock, patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import ResolutionNotFound
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue
from supervisor.resolution.validate import get_valid_modules


@pytest.fixture(autouse=True)
def fixture_mock_dns_query():
    """Mock aiodns query."""
    with (
        patch(
            "supervisor.resolution.checks.dns_server.DNSResolver.query",
            new_callable=AsyncMock,
        ),
        patch(
            "supervisor.resolution.checks.dns_server_ipv6.DNSResolver.query",
            new_callable=AsyncMock,
        ),
    ):
        yield


async def test_check_setup(coresys: CoreSys):
    """Test check for setup."""
    await coresys.core.set_state(CoreState.SETUP)
    with patch(
        "supervisor.resolution.checks.free_space.CheckFreeSpace.run_check",
        return_value=False,
    ) as free_space:
        await coresys.resolution.check.check_system()
        free_space.assert_not_called()


async def test_check_running(coresys: CoreSys):
    """Test check for setup."""
    await coresys.core.set_state(CoreState.RUNNING)
    with patch(
        "supervisor.resolution.checks.free_space.CheckFreeSpace.run_check",
        return_value=False,
    ) as free_space:
        await coresys.resolution.check.check_system()
        free_space.assert_called_once()


async def test_if_check_make_issue(coresys: CoreSys):
    """Test check for setup."""
    free_space = Issue(IssueType.FREE_SPACE, ContextType.SYSTEM)
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.security.content_trust = False

    with patch("shutil.disk_usage", return_value=(1, 1, 1)):
        await coresys.resolution.check.check_system()

    assert free_space in coresys.resolution.issues


async def test_if_check_cleanup_issue(coresys: CoreSys):
    """Test check for setup."""
    free_space = Issue(IssueType.FREE_SPACE, ContextType.SYSTEM)
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.security.content_trust = False

    with patch("shutil.disk_usage", return_value=(1, 1, 1)):
        await coresys.resolution.check.check_system()

    assert free_space in coresys.resolution.issues

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        await coresys.resolution.check.check_system()

    assert free_space not in coresys.resolution.issues


async def test_enable_disable_checks(coresys: CoreSys):
    """Test enable and disable check."""
    await coresys.core.set_state(CoreState.RUNNING)
    free_space = coresys.resolution.check.get("free_space")

    # Ensure the check was enabled
    assert free_space.enabled

    free_space.enabled = False
    assert not free_space.enabled

    with patch(
        "supervisor.resolution.checks.free_space.CheckFreeSpace.run_check",
        return_value=False,
    ) as free_space:
        await coresys.resolution.check.check_system()
        free_space.assert_not_called()

    free_space.enabled = True
    assert free_space.enabled


async def test_get_checks(coresys: CoreSys):
    """Test get check with slug."""

    with pytest.raises(ResolutionNotFound):
        coresys.resolution.check.get("does_not_exsist")

    assert coresys.resolution.check.get("free_space")


async def test_dynamic_check_loader(coresys: CoreSys):
    """Test dynamic check loader, this ensures that all checks have defined a setup function."""

    def load_modules():
        coresys.resolution.check.load_modules()
        return get_valid_modules("checks")

    for check in await coresys.run_in_executor(load_modules):
        assert check in coresys.resolution.check._checks
