"""Test discovery API."""

import logging
from unittest.mock import MagicMock, patch
from uuid import uuid4

from aiohttp.test_utils import TestClient
import pytest

from supervisor.addons.addon import Addon
from supervisor.discovery import Discovery


@pytest.mark.parametrize("api_client", ["local_ssh"], indirect=True)
async def test_discovery_forbidden(
    api_client: TestClient, caplog: pytest.LogCaptureFixture, install_addon_ssh
):
    """Test addon sending discovery message for an unregistered service."""
    caplog.clear()

    with caplog.at_level(logging.ERROR):
        resp = await api_client.post("/discovery", json={"service": "mqtt"})

    assert resp.status == 400
    result = await resp.json()
    assert result["result"] == "error"
    assert (
        result["message"]
        == "Add-ons must list services they provide via discovery in their config!"
    )
    assert "Please report this to the maintainer of the add-on" in caplog.text


@pytest.mark.parametrize("api_client", ["local_ssh"], indirect=True)
async def test_discovery_unknown_service(
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
