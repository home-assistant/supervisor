"""Tests for Home Assistant API port conflict dispatch."""

# pylint: disable=protected-access

from unittest.mock import AsyncMock, patch

from aiohttp.test_utils import TestClient

from supervisor.const import AppState
from supervisor.coresys import CoreSys
from supervisor.docker.manager import IPV4_WILDCARD, IPV6_WILDCARD, DockerPortBinding
from supervisor.exceptions import AppsError
from supervisor.homeassistant.core import ComponentType
from supervisor.homeassistant.module import HomeAssistant
from supervisor.resolution.const import IssueType, SuggestionType


async def test_api_set_options_port_no_conflict(
    core_api_client_with_root: tuple[TestClient, str],
    coresys: CoreSys,
):
    """Test setting port with no conflicts does not dispatch a conflict."""
    api_client, root = core_api_client_with_root
    new_port = 18123

    used_bindings = {
        DockerPortBinding(
            ip=IPV4_WILDCARD,
            public_port=new_port + 1,
            type="tcp",
            private_port=new_port + 1,
        ): "other-container"
    }

    with (
        patch.object(HomeAssistant, "save_data"),
        patch.object(
            coresys.apps,
            "get_used_host_port_bindings",
            AsyncMock(return_value=used_bindings),
        ),
        patch.object(
            coresys.homeassistant.core,
            "set_port_conflict",
            AsyncMock(),
        ) as set_port_conflict,
    ):
        resp = await api_client.post(f"{root}/options", json={"port": new_port})

    assert resp.status == 200
    set_port_conflict.assert_not_awaited()


async def test_api_set_options_port_conflict_with_app(
    core_api_client_with_root: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_ssh,
):
    """Test setting port dispatches app conflict when app binds requested port."""
    api_client, root = core_api_client_with_root
    new_port = 18124

    used_bindings = {
        DockerPortBinding(
            ip=IPV4_WILDCARD,
            public_port=new_port,
            type="tcp",
            private_port=new_port,
        ): install_app_ssh.instance.name
    }

    with (
        patch.object(HomeAssistant, "save_data"),
        patch.object(
            coresys.apps,
            "get_used_host_port_bindings",
            AsyncMock(return_value=used_bindings),
        ),
        patch.object(
            coresys.homeassistant.core,
            "set_port_conflict",
            AsyncMock(),
        ) as set_port_conflict,
    ):
        resp = await api_client.post(f"{root}/options", json={"port": new_port})

    assert resp.status == 200
    set_port_conflict.assert_awaited_once()
    conflict = set_port_conflict.await_args.args[0]
    assert conflict.component_type == ComponentType.APP
    assert conflict.component is install_app_ssh
    assert conflict.port == new_port


async def test_api_set_options_port_conflict_with_plugin(
    core_api_client_with_root: tuple[TestClient, str],
    coresys: CoreSys,
):
    """Test setting port dispatches plugin conflict when plugin binds requested port."""
    api_client, root = core_api_client_with_root
    new_port = 18125
    plugin = coresys.plugins.dns

    used_bindings = {
        DockerPortBinding(
            ip=IPV4_WILDCARD,
            public_port=new_port,
            type="tcp",
            private_port=new_port,
        ): plugin.instance.name
    }

    with (
        patch.object(HomeAssistant, "save_data"),
        patch.object(
            coresys.apps,
            "get_used_host_port_bindings",
            AsyncMock(return_value=used_bindings),
        ),
        patch.object(
            coresys.homeassistant.core,
            "set_port_conflict",
            AsyncMock(),
        ) as set_port_conflict,
    ):
        resp = await api_client.post(f"{root}/options", json={"port": new_port})

    assert resp.status == 200
    set_port_conflict.assert_awaited_once()
    conflict = set_port_conflict.await_args.args[0]
    assert conflict.component_type == ComponentType.PLUGIN
    assert conflict.component is plugin
    assert conflict.port == new_port


async def test_api_set_options_port_conflict_with_unknown_component(
    core_api_client_with_root: tuple[TestClient, str],
    coresys: CoreSys,
):
    """Test setting port dispatches unknown conflict when name is not app/plugin."""
    api_client, root = core_api_client_with_root
    new_port = 18126
    unknown_name = "external-process"

    used_bindings = {
        DockerPortBinding(
            ip=IPV4_WILDCARD,
            public_port=new_port,
            type="tcp",
            private_port=new_port,
        ): unknown_name
    }

    with (
        patch.object(HomeAssistant, "save_data"),
        patch.object(
            coresys.apps,
            "get_used_host_port_bindings",
            AsyncMock(return_value=used_bindings),
        ),
        patch.object(
            coresys.homeassistant.core,
            "set_port_conflict",
            AsyncMock(),
        ) as set_port_conflict,
    ):
        resp = await api_client.post(f"{root}/options", json={"port": new_port})

    assert resp.status == 200
    set_port_conflict.assert_awaited_once()
    conflict = set_port_conflict.await_args.args[0]
    assert conflict.component_type == ComponentType.UNKNOWN
    assert conflict.component == unknown_name
    assert conflict.port == new_port


async def test_api_set_options_port_conflict_dual_stack_dispatches_twice(
    core_api_client_with_root: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_ssh,
):
    """Test v4+v6 conflicting bindings currently dispatch two conflict callbacks."""
    api_client, root = core_api_client_with_root
    new_port = 18127

    used_bindings = {
        DockerPortBinding(
            ip=IPV4_WILDCARD,
            public_port=new_port,
            type="tcp",
            private_port=new_port,
        ): install_app_ssh.instance.name,
        DockerPortBinding(
            ip=IPV6_WILDCARD,
            public_port=new_port,
            type="tcp",
            private_port=new_port,
        ): install_app_ssh.instance.name,
    }

    with (
        patch.object(HomeAssistant, "save_data"),
        patch.object(
            coresys.apps,
            "get_used_host_port_bindings",
            AsyncMock(return_value=used_bindings),
        ),
        patch.object(
            coresys.homeassistant.core,
            "set_port_conflict",
            AsyncMock(),
        ) as set_port_conflict,
    ):
        resp = await api_client.post(f"{root}/options", json={"port": new_port})

    assert resp.status == 200
    assert set_port_conflict.await_count == 2


async def test_api_set_options_port_conflict_integration_stopped_app_creates_issue_only(
    core_api_client_with_root: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_ssh,
):
    """Stopped app conflict should create issue but not stop app or abort startup."""
    api_client, root = core_api_client_with_root
    new_port = 18128
    install_app_ssh.state = AppState.STOPPED
    install_app_ssh.persist["network"] = {"22/tcp": new_port}

    used_bindings = {
        DockerPortBinding(
            ip=IPV4_WILDCARD,
            public_port=new_port,
            type="tcp",
            private_port=new_port,
        ): install_app_ssh.instance.name
    }

    coresys.homeassistant.core._startup_abort = AsyncMock()
    with (
        patch.object(HomeAssistant, "save_data"),
        patch.object(
            coresys.apps,
            "get_used_host_port_bindings",
            AsyncMock(return_value=used_bindings),
        ),
        patch.object(install_app_ssh, "stop", AsyncMock()) as app_stop,
    ):
        resp = await api_client.post(f"{root}/options", json={"port": new_port})

    assert resp.status == 200
    app_stop.assert_not_awaited()
    coresys.homeassistant.core._startup_abort.set.assert_not_called()
    assert any(
        issue.type == IssueType.APP_PORT_CONFLICT_CORE
        and issue.reference == install_app_ssh.slug
        and issue.reference_extra == {"port": new_port}
        for issue in coresys.resolution.issues
    )
    assert any(
        suggestion.type == SuggestionType.CLEAR_PORT_CONFIG
        and suggestion.reference == install_app_ssh.slug
        and suggestion.reference_extra == {"port": new_port}
        for suggestion in coresys.resolution.suggestions
    )


async def test_api_set_options_port_conflict_integration_running_app_stops(
    core_api_client_with_root: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_ssh,
):
    """Running app conflict should try stopping app and create an issue."""
    api_client, root = core_api_client_with_root
    new_port = 18129
    install_app_ssh.state = AppState.STARTED
    install_app_ssh.persist["network"] = {"22/tcp": new_port}

    used_bindings = {
        DockerPortBinding(
            ip=IPV4_WILDCARD,
            public_port=new_port,
            type="tcp",
            private_port=new_port,
        ): install_app_ssh.instance.name
    }

    with (
        patch.object(HomeAssistant, "save_data"),
        patch.object(
            coresys.apps,
            "get_used_host_port_bindings",
            AsyncMock(return_value=used_bindings),
        ),
        patch.object(install_app_ssh, "stop", AsyncMock()) as app_stop,
    ):
        resp = await api_client.post(f"{root}/options", json={"port": new_port})

    assert resp.status == 200
    app_stop.assert_awaited_once()
    assert any(
        issue.type == IssueType.APP_PORT_CONFLICT_CORE
        and issue.reference == install_app_ssh.slug
        and issue.reference_extra == {"port": new_port}
        for issue in coresys.resolution.issues
    )


async def test_api_set_options_port_conflict_integration_aborts_if_unresolved(
    core_api_client_with_root: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_ssh,
):
    """Running app conflict should abort startup sequence if stop fails."""
    api_client, root = core_api_client_with_root
    new_port = 18130
    install_app_ssh.state = AppState.STARTED

    used_bindings = {
        DockerPortBinding(
            ip=IPV4_WILDCARD,
            public_port=new_port,
            type="tcp",
            private_port=new_port,
        ): install_app_ssh.instance.name
    }

    coresys.homeassistant.core._startup_abort = AsyncMock()
    with (
        patch.object(HomeAssistant, "save_data"),
        patch.object(
            coresys.apps,
            "get_used_host_port_bindings",
            AsyncMock(return_value=used_bindings),
        ),
        patch.object(install_app_ssh, "stop", AsyncMock(side_effect=AppsError())),
    ):
        resp = await api_client.post(f"{root}/options", json={"port": new_port})

    assert resp.status == 200
    coresys.homeassistant.core._startup_abort.set.assert_called_once()
