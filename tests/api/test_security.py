"""Test API security layer."""

from aiohttp import web
import pytest

from supervisor.api import RestAPI
from supervisor.const import CoreState
from supervisor.coresys import CoreSys

# pylint: disable=redefined-outer-name


@pytest.fixture
async def api_system(aiohttp_client, run_dir, coresys: CoreSys):
    """Fixture for RestAPI client."""
    api = RestAPI(coresys)
    api.webapp = web.Application()
    await api.load()

    api.webapp.middlewares.append(api.security.system_validation)
    yield await aiohttp_client(api.webapp)


@pytest.mark.asyncio
async def test_api_security_system_initialize(api_system, coresys: CoreSys):
    """Test security."""
    coresys.core.state = CoreState.INITIALIZE

    resp = await api_system.get("/supervisor/ping")
    result = await resp.json()
    assert resp.status == 400
    assert result["result"] == "error"


@pytest.mark.asyncio
async def test_api_security_system_running(api_system, coresys: CoreSys):
    """Test security."""
    coresys.core.state = CoreState.RUNNING

    resp = await api_system.get("/supervisor/ping")
    assert resp.status == 200


@pytest.mark.asyncio
async def test_api_security_system_setup(api_system, coresys: CoreSys):
    """Test security."""
    coresys.core.state = CoreState.SETUP

    resp = await api_system.get("/supervisor/ping")
    assert resp.status == 200
