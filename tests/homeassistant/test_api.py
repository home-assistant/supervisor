"""Test Home Assistant API."""

from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch

from aiohttp import hdrs
from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import HomeAssistantAPIError
from supervisor.homeassistant.const import LANDINGPAGE


async def test_check_frontend_available_success(coresys: CoreSys):
    """Test frontend availability check succeeds with valid HTML response."""
    coresys.homeassistant.version = AwesomeVersion("2025.8.0")

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {hdrs.CONTENT_TYPE: "text/html; charset=utf-8"}

    @asynccontextmanager
    async def mock_make_request(*args, **kwargs):
        yield mock_response

    with patch.object(
        type(coresys.homeassistant.api), "make_request", new=mock_make_request
    ):
        result = await coresys.homeassistant.api.check_frontend_available()

    assert result is True


async def test_check_frontend_available_wrong_status(coresys: CoreSys):
    """Test frontend availability check fails with non-200 status."""
    coresys.homeassistant.version = AwesomeVersion("2025.8.0")

    mock_response = MagicMock()
    mock_response.status = 404
    mock_response.headers = {hdrs.CONTENT_TYPE: "text/html"}

    @asynccontextmanager
    async def mock_make_request(*args, **kwargs):
        yield mock_response

    with patch.object(
        type(coresys.homeassistant.api), "make_request", new=mock_make_request
    ):
        result = await coresys.homeassistant.api.check_frontend_available()

    assert result is False


async def test_check_frontend_available_wrong_content_type(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test frontend availability check fails with wrong content type."""
    coresys.homeassistant.version = AwesomeVersion("2025.8.0")

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {hdrs.CONTENT_TYPE: "application/json"}

    @asynccontextmanager
    async def mock_make_request(*args, **kwargs):
        yield mock_response

    with patch.object(
        type(coresys.homeassistant.api), "make_request", new=mock_make_request
    ):
        result = await coresys.homeassistant.api.check_frontend_available()

    assert result is False
    assert "unexpected content type" in caplog.text


async def test_check_frontend_available_api_error(coresys: CoreSys):
    """Test frontend availability check handles API errors gracefully."""
    coresys.homeassistant.version = AwesomeVersion("2025.8.0")

    @asynccontextmanager
    async def mock_make_request(*args, **kwargs):
        raise HomeAssistantAPIError("Connection failed")
        yield  # pragma: no cover

    with patch.object(
        type(coresys.homeassistant.api), "make_request", new=mock_make_request
    ):
        result = await coresys.homeassistant.api.check_frontend_available()

    assert result is False


async def test_check_frontend_available_landingpage(coresys: CoreSys):
    """Test frontend availability check returns False for landingpage."""
    coresys.homeassistant.version = LANDINGPAGE

    result = await coresys.homeassistant.api.check_frontend_available()

    assert result is False


async def test_check_frontend_available_no_version(coresys: CoreSys):
    """Test frontend availability check returns False when no version set."""
    coresys.homeassistant.version = None

    result = await coresys.homeassistant.api.check_frontend_available()

    assert result is False
