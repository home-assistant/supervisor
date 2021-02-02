"""Test API security layer."""

from unittest.mock import patch

from aiohttp import web
import pytest

from supervisor.addons.addon import Addon
from supervisor.api import RestAPI
from supervisor.const import HEADER_TOKEN

# pylint: disable=redefined-outer-name


@pytest.fixture
async def api_deprecation(aiohttp_client, coresys):
    """Fixture for RestAPI client."""
    api = RestAPI(coresys)
    api.webapp = web.Application()
    await api.load()

    api.webapp.middlewares.append(api.security.token_validation)
    api.webapp.middlewares.append(api.deprecation.check_deprecation)
    yield await aiohttp_client(api.webapp)


@pytest.mark.asyncio
async def test_api_from_home_assistant(api_deprecation, caplog):
    """Test access to non deprecated API."""

    resp = await api_deprecation.get("/supervisor/ping")
    assert resp.status == 200
    assert not caplog.messages


@pytest.mark.asyncio
async def test_deprecated_api_from_home_assistant(api_deprecation, coresys, caplog):
    """Test deprecated API access from Home Assistant."""
    coresys.homeassistant.supervisor_token = "xxx"

    resp = await api_deprecation.post(
        "/hardware/trigger",
        headers={HEADER_TOKEN: coresys.homeassistant.supervisor_token},
    )
    assert resp.status == 200
    assert "Access to deprecated API '/hardware/trigger'" in caplog.messages[0]


@pytest.mark.asyncio
async def test_deprecated_api_from_addon(api_deprecation, coresys, caplog):
    """Test deprecated API access from Addon."""
    addon = Addon(coresys, "example")
    coresys.addons.local[addon.slug] = addon
    coresys.addons.data._data["system"] = {"example": {"name": "example"}}

    with patch("supervisor.addons.addon.Addon.supervisor_token", "xxx"):

        resp = await api_deprecation.post(
            "/hardware/trigger", headers={HEADER_TOKEN: "xxx"}
        )
        assert resp.status == 200
        assert (
            "Access to deprecated API '/hardware/trigger' detected from example - please report this to the maintainer of the example add-on"
            in caplog.messages[0]
        )


@pytest.mark.asyncio
async def test_deprecated_api_from_addon_with_update(api_deprecation, coresys, caplog):
    """Test deprecated API access from Addon with update."""
    addon = Addon(coresys, "example")
    coresys.addons.local[addon.slug] = addon
    coresys.addons.data._data["system"] = {"example": {"name": "example"}}

    with patch("supervisor.addons.addon.Addon.supervisor_token", "xxx"), patch(
        "supervisor.addons.addon.Addon.need_update", True
    ), patch("supervisor.addons.addon.Addon.version", "1.0.0"), patch(
        "supervisor.addons.addon.Addon.latest_version", "1.0.1"
    ):

        resp = await api_deprecation.post(
            "/hardware/trigger", headers={HEADER_TOKEN: "xxx"}
        )
        assert resp.status == 200
        assert (
            "Access to deprecated API '/hardware/trigger' detected from example - you are currently running version 1.0.0, there is an update pending for 1.0.1. If that does not help please report this to the maintainer of the example add-on"
            in caplog.messages[0]
        )
