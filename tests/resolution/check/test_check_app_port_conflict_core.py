"""Test app port conflict with core check."""

# pylint: disable=protected-access

from unittest.mock import AsyncMock

from supervisor.const import AppState
from supervisor.resolution.checks.app_port_conflict_core import CheckAppPortConflictCore


async def test_approve_check_missing_reference_data(coresys):
    """Test approval fails if required fields are missing."""
    check = CheckAppPortConflictCore(coresys)

    assert not await check.approve_check(None, {"port": coresys.homeassistant.api_port})
    assert not await check.approve_check("test", None)
    assert not await check.approve_check("test", {"other": 1234})


async def test_approve_check_homeassistant_port_changed(coresys, install_app_ssh):
    """Test approval fails if Home Assistant changed API port."""
    check = CheckAppPortConflictCore(coresys)
    app = install_app_ssh

    assert not await check.approve_check(
        app.slug,
        {"port": coresys.homeassistant.api_port + 1},
    )


async def test_approve_check_uninstalled_app(coresys):
    """Test approval fails for uninstalled app."""
    check = CheckAppPortConflictCore(coresys)

    assert not await check.approve_check(
        "missing-app",
        {"port": coresys.homeassistant.api_port},
    )


async def test_approve_check_resolved_when_app_running_and_core_up(
    coresys, install_app_ssh
):
    """Test approval fails when conflict is considered resolved."""
    check = CheckAppPortConflictCore(coresys)
    app = install_app_ssh
    app.state = AppState.STARTED
    coresys.homeassistant.api.check_api_state = AsyncMock(return_value=True)

    assert not await check.approve_check(
        app.slug,
        {"port": coresys.homeassistant.api_port},
    )


async def test_approve_check_host_network_app_still_affected(coresys, install_app_ssh):
    """Test host network app is considered still affected."""
    check = CheckAppPortConflictCore(coresys)
    app = install_app_ssh
    app.state = AppState.STOPPED
    app.data["host_network"] = True

    assert await check.approve_check(
        app.slug,
        {"port": coresys.homeassistant.api_port},
    )


async def test_approve_check_port_mapping_still_present(coresys, install_app_ssh):
    """Test app is affected if conflicting mapping is still configured."""
    check = CheckAppPortConflictCore(coresys)
    app = install_app_ssh
    app.state = AppState.STOPPED

    app.persist["network"] = {"8123/tcp": coresys.homeassistant.api_port}

    assert await check.approve_check(
        app.slug,
        {"port": coresys.homeassistant.api_port},
    )
