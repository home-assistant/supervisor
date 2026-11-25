"""Test check for apps still calling Supervisor over TCP."""

from unittest.mock import patch

import pytest

from supervisor.apps.app import App
from supervisor.const import CoreState, UpdateChannel
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.deprecated_tcp_api_app import CheckDeprecatedTcpApiApp
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue


def _issue(slug: str, version: str = "9.2.1") -> Issue:
    """Return the TCP API deprecation issue for an app version."""
    return Issue(
        IssueType.DEPRECATED_TCP_API_REQUEST,
        ContextType.ADDON,
        reference=slug,
        reference_extra={"version": version},
    )


async def test_base(coresys: CoreSys):
    """Test check basics."""
    check = CheckDeprecatedTcpApiApp(coresys)
    assert check.slug == "deprecated_tcp_api_app"
    assert check.enabled


async def test_check_raises_nothing(coresys: CoreSys, install_app_ssh: App):
    """Test the check leaves raising the repair to the security middleware."""
    await coresys.core.set_state(CoreState.RUNNING)

    await CheckDeprecatedTcpApiApp(coresys)()

    assert coresys.resolution.issues == []


@pytest.mark.parametrize(
    ("config", "channel", "version", "approved"),
    [
        pytest.param({}, UpdateChannel.STABLE, "9.2.1", True, id="default"),
        pytest.param(
            {"supervisor_api_tcp": True}, UpdateChannel.STABLE, "9.2.1", True, id="tcp"
        ),
        pytest.param(
            {"supervisor_api_tcp": False},
            UpdateChannel.STABLE,
            "9.2.1",
            False,
            id="socket",
        ),
        pytest.param({}, UpdateChannel.STABLE, "9.2.0", False, id="updated"),
        pytest.param(
            {"repository": "a0d7b954"},
            UpdateChannel.DEV,
            "9.2.1",
            True,
            id="dev-channel",
        ),
        pytest.param(
            {"repository": "a0d7b954"},
            UpdateChannel.STABLE,
            "9.2.1",
            False,
            id="left-dev-channel",
        ),
    ],
)
async def test_approve(
    coresys: CoreSys,
    install_app_ssh: App,
    config: dict[str, bool | str],
    channel: UpdateChannel,
    version: str,
    approved: bool,
):
    """Test the repair stays only while it applies to this app version and user."""
    install_app_ssh.data.update(config)
    coresys.updater.channel = channel

    check = CheckDeprecatedTcpApiApp(coresys)
    assert await check.approve_check(_issue(install_app_ssh.slug, version)) is approved


async def test_approve_without_version(coresys: CoreSys, install_app_ssh: App):
    """Test a repair without the app version is dropped."""
    issue = Issue(
        IssueType.DEPRECATED_TCP_API_REQUEST,
        ContextType.ADDON,
        reference=install_app_ssh.slug,
    )

    check = CheckDeprecatedTcpApiApp(coresys)
    assert await check.approve_check(issue) is False


async def test_approve_uninstalled(coresys: CoreSys):
    """Test the repair is dropped for an app that is no longer installed."""
    check = CheckDeprecatedTcpApiApp(coresys)
    assert await check.approve_check(_issue("local_ssh")) is False


async def test_dismissed_when_tcp_disabled(coresys: CoreSys, install_app_ssh: App):
    """Test the repair is dismissed once the app sets supervisor_api_tcp false."""
    coresys.resolution.add_issue(_issue(install_app_ssh.slug))
    await coresys.core.set_state(CoreState.RUNNING)
    check = CheckDeprecatedTcpApiApp(coresys)
    await check()
    assert _issue(install_app_ssh.slug) in coresys.resolution.issues

    install_app_ssh.data["supervisor_api_tcp"] = False
    await check()

    assert _issue(install_app_ssh.slug) not in coresys.resolution.issues


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    check = CheckDeprecatedTcpApiApp(coresys)
    should_run = check.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert should_run == [CoreState.RUNNING]
    assert len(should_not_run) != 0

    with patch.object(CheckDeprecatedTcpApiApp, "run_check", return_value=None) as run:
        for state in should_run:
            await coresys.core.set_state(state)
            await check()
            run.assert_called_once()
            run.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await check()
            run.assert_not_called()
            run.reset_mock()
