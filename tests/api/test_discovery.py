"""Test discovery API."""

import logging
from unittest.mock import ANY, MagicMock, patch
from uuid import uuid4

from aiohttp.test_utils import TestClient
import pytest

from supervisor.addons.addon import Addon
from supervisor.const import AddonState
from supervisor.coresys import CoreSys
from supervisor.discovery import Discovery, Message

from tests.common import load_json_fixture


@pytest.mark.parametrize("api_client", ["local_ssh"], indirect=True)
async def test_api_discovery_forbidden(
    api_client: TestClient, caplog: pytest.LogCaptureFixture, install_addon_ssh
):
    """Test addon sending discovery message for an unregistered service."""
    caplog.clear()

    with caplog.at_level(logging.ERROR):
        resp = await api_client.post("/discovery", json={"service": "mqtt"})

    assert resp.status == 403
    result = await resp.json()
    assert result["result"] == "error"
    assert (
        result["message"]
        == "Add-ons must list services they provide via discovery in their config!"
    )
    assert "Please report this to the maintainer of the add-on" in caplog.text


@pytest.mark.parametrize("api_client", ["local_ssh"], indirect=True)
async def test_api_discovery_unknown_service(
    api_client: TestClient, caplog: pytest.LogCaptureFixture, install_addon_ssh: Addon
):
    """Test addon sending discovery message for an unkown service."""
    caplog.clear()
    install_addon_ssh.data["discovery"] = ["junk"]

    message = MagicMock()
    message.uuid = uuid4().hex

    with caplog.at_level(logging.WARNING), patch.object(
        Discovery, "send", return_value=message
    ):
        resp = await api_client.post("/discovery", json={"service": "junk"})

    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["uuid"] == message.uuid
    assert "Please report this to the maintainer of the add-on" in caplog.text


@pytest.mark.parametrize(
    "skip_state", [AddonState.ERROR, AddonState.STOPPED, AddonState.STARTUP]
)
async def test_api_list_discovery(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_ssh: Addon,
    skip_state: AddonState,
):
    """Test listing discovery messages only returns ones for healthy services."""
    with patch(
        "supervisor.utils.common.read_json_or_yaml_file",
        return_value=load_json_fixture("discovery.json"),
    ), patch("supervisor.utils.common.Path.is_file", return_value=True):
        coresys.discovery.read_data()

    await coresys.discovery.load()
    assert coresys.discovery.list_messages == [
        Message(addon="core_mosquitto", service="mqtt", config=ANY, uuid=ANY),
        Message(addon="local_ssh", service="adguard", config=ANY, uuid=ANY),
    ]

    install_addon_ssh.state = AddonState.STARTED
    resp = await api_client.get("/discovery")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["discovery"] == [
        {
            "addon": "local_ssh",
            "service": "adguard",
            "config": ANY,
            "uuid": ANY,
        }
    ]

    install_addon_ssh.state = skip_state
    resp = await api_client.get("/discovery")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["discovery"] == []
