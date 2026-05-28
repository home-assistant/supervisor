"""Test discovery API."""

import logging
from unittest.mock import ANY, AsyncMock, MagicMock, patch

from aiohttp.test_utils import TestClient
import pytest

from supervisor.apps.app import App
from supervisor.const import AppState
from supervisor.coresys import CoreSys
from supervisor.discovery import Message

from tests.common import force_app_state, load_json_fixture


async def test_api_discovery_forbidden(
    app_api_client_with_prefix: tuple[TestClient, str],
    caplog: pytest.LogCaptureFixture,
):
    """Test app sending discovery message for an unregistered service."""
    api_client, prefix = app_api_client_with_prefix
    caplog.clear()

    with caplog.at_level(logging.ERROR):
        resp = await api_client.post(
            f"{prefix}/discovery", json={"service": "mqtt", "config": {}}
        )

    assert resp.status == 403
    result = await resp.json()
    assert result["result"] == "error"
    assert (
        result["message"]
        == "Apps must list services they provide via discovery in their config!"
    )
    assert "Please report this to the maintainer of the app" in caplog.text


@pytest.mark.parametrize(
    "skip_state", [AppState.ERROR, AppState.STOPPED, AppState.STARTUP]
)
async def test_api_list_discovery(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_ssh: App,
    skip_state: AppState,
):
    """Test listing discovery messages only returns ones for healthy services."""
    api_client, prefix = api_client_with_prefix
    with (
        patch(
            "supervisor.utils.common.read_json_or_yaml_file",
            return_value=load_json_fixture("discovery.json"),
        ),
        patch("supervisor.utils.common.Path.is_file", return_value=True),
    ):
        await coresys.discovery.read_data()

    await coresys.discovery.load()
    assert coresys.discovery.list_messages == [
        Message(app="core_mosquitto", service="mqtt", config=ANY, uuid=ANY),
        Message(app="local_ssh", service="adguard", config=ANY, uuid=ANY),
    ]

    force_app_state(install_app_ssh, AppState.STARTED)
    resp = await api_client.get(f"{prefix}/discovery")
    assert resp.status == 200
    result = await resp.json()
    app_key = "app" if prefix == "/v2" else "addon"
    assert result["data"]["discovery"] == [
        {
            app_key: "local_ssh",
            "service": "adguard",
            "config": ANY,
            "uuid": ANY,
        }
    ]

    force_app_state(install_app_ssh, skip_state)
    resp = await api_client.get(f"{prefix}/discovery")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["discovery"] == []


async def test_api_send_del_discovery(
    app_api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_ssh: App,
    websession: MagicMock,
):
    """Test adding and removing discovery."""
    api_client, prefix = app_api_client_with_prefix
    install_app_ssh.data["discovery"] = ["test"]
    coresys.homeassistant.api._ensure_access_token = AsyncMock()  # pylint: disable=protected-access

    resp = await api_client.post(
        f"{prefix}/discovery", json={"service": "test", "config": {}}
    )
    assert resp.status == 200
    result = await resp.json()
    uuid = result["data"]["uuid"]
    coresys.websession.request.assert_called_once()
    assert coresys.websession.request.call_args.args[0] == "post"
    assert (
        coresys.websession.request.call_args.args[1]
        == f"http://172.30.32.1:8123/api/hassio_push/discovery/{uuid}"
    )
    assert coresys.websession.request.call_args.kwargs["json"] == {
        "addon": install_app_ssh.slug,
        "service": "test",
        "uuid": uuid,
    }

    message = coresys.discovery.get(uuid)
    assert message.app == install_app_ssh.slug
    assert message.service == "test"
    assert message.config == {}

    coresys.websession.request.reset_mock()
    resp = await api_client.delete(f"{prefix}/discovery/{uuid}")
    assert resp.status == 200
    coresys.websession.request.assert_called_once()
    assert coresys.websession.request.call_args.args[0] == "delete"
    assert (
        coresys.websession.request.call_args.args[1]
        == f"http://172.30.32.1:8123/api/hassio_push/discovery/{uuid}"
    )
    assert coresys.websession.request.call_args.kwargs["json"] == {
        "addon": install_app_ssh.slug,
        "service": "test",
        "uuid": uuid,
    }

    assert coresys.discovery.get(uuid) is None


async def test_api_invalid_discovery(
    app_api_client_with_prefix: tuple[TestClient, str],
    install_app_ssh: App,
):
    """Test invalid discovery messages."""
    api_client, prefix = app_api_client_with_prefix
    install_app_ssh.data["discovery"] = ["test"]

    resp = await api_client.post(f"{prefix}/discovery", json={"service": "test"})
    assert resp.status == 400

    resp = await api_client.post(
        f"{prefix}/discovery", json={"service": "test", "config": None}
    )
    assert resp.status == 400


async def test_discovery_not_found_get(
    api_client_with_prefix: tuple[TestClient, str],
):
    """Test GET /discovery/{uuid} returns 404 for an unknown uuid."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.get(f"{prefix}/discovery/bad")
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Discovery message not found"


async def test_discovery_not_found_delete(
    app_api_client_with_prefix: tuple[TestClient, str],
):
    """Test DELETE /discovery/{uuid} returns 404 for an unknown uuid."""
    api_client, prefix = app_api_client_with_prefix
    resp = await api_client.delete(f"{prefix}/discovery/bad")
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Discovery message not found"


async def test_get_discovery_v1_v2_keys(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    install_app_ssh: App,
):
    """Test GET /discovery/{uuid} returns 'addon' key on V1 and 'app' key on V2."""
    api_client, prefix = api_client_with_prefix

    # Seed a discovery message directly (bypass the HA push)
    message = await coresys.discovery.send(
        install_app_ssh, "adguard", {"host": "127.0.0.1", "port": 3000}
    )
    uuid = message.uuid

    resp = await api_client.get(f"{prefix}/discovery/{uuid}")
    assert resp.status == 200
    result = await resp.json()

    app_key = "app" if prefix == "/v2" else "addon"
    absent_key = "addon" if prefix == "/v2" else "app"
    assert result["data"][app_key] == install_app_ssh.slug
    assert absent_key not in result["data"]
    assert result["data"]["service"] == "adguard"
    assert result["data"]["uuid"] == uuid
