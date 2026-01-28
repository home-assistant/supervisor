"""Test Home Assistant API."""

from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch

from aiohttp import hdrs
from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import HomeAssistantAPIError


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


async def test_get_config_success(coresys: CoreSys):
    """Test get_config returns valid config dictionary."""
    coresys.homeassistant.version = AwesomeVersion("2025.8.0")

    expected_config = {
        "latitude": 32.87336,
        "longitude": -117.22743,
        "elevation": 0,
        "unit_system": {
            "length": "km",
            "mass": "g",
            "temperature": "°C",
            "volume": "L",
        },
        "location_name": "Home",
        "time_zone": "America/Los_Angeles",
        "components": ["frontend", "config"],
        "version": "2025.8.0",
    }

    mock_response = MagicMock()
    mock_response.status = 200

    async def mock_json():
        return expected_config

    mock_response.json = mock_json

    @asynccontextmanager
    async def mock_make_request(*_args, **_kwargs):
        yield mock_response

    with patch.object(
        type(coresys.homeassistant.api), "make_request", new=mock_make_request
    ):
        result = await coresys.homeassistant.api.get_config()

    assert result == expected_config


async def test_get_config_returns_none(coresys: CoreSys):
    """Test get_config raises error when None is returned."""
    coresys.homeassistant.version = AwesomeVersion("2025.8.0")

    mock_response = MagicMock()
    mock_response.status = 200

    async def mock_json():
        return None

    mock_response.json = mock_json

    @asynccontextmanager
    async def mock_make_request(*_args, **_kwargs):
        yield mock_response

    with (
        patch.object(
            type(coresys.homeassistant.api), "make_request", new=mock_make_request
        ),
        pytest.raises(
            HomeAssistantAPIError, match="No config received from Home Assistant API"
        ),
    ):
        await coresys.homeassistant.api.get_config()


async def test_get_config_returns_non_dict(coresys: CoreSys):
    """Test get_config raises error when non-dict is returned."""
    coresys.homeassistant.version = AwesomeVersion("2025.8.0")

    mock_response = MagicMock()
    mock_response.status = 200

    async def mock_json():
        return ["not", "a", "dict"]

    mock_response.json = mock_json

    @asynccontextmanager
    async def mock_make_request(*_args, **_kwargs):
        yield mock_response

    with (
        patch.object(
            type(coresys.homeassistant.api), "make_request", new=mock_make_request
        ),
        pytest.raises(
            HomeAssistantAPIError, match="No config received from Home Assistant API"
        ),
    ):
        await coresys.homeassistant.api.get_config()


async def test_get_config_api_error(coresys: CoreSys):
    """Test get_config propagates API errors from underlying _get_json call."""
    coresys.homeassistant.version = AwesomeVersion("2025.8.0")

    mock_response = MagicMock()
    mock_response.status = 500

    @asynccontextmanager
    async def mock_make_request(*_args, **_kwargs):
        yield mock_response

    with (
        patch.object(
            type(coresys.homeassistant.api), "make_request", new=mock_make_request
        ),
        pytest.raises(
            HomeAssistantAPIError, match="Home Assistant Core API return 500"
        ),
    ):
        await coresys.homeassistant.api.get_config()
