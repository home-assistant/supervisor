"""Test haveibeenpwned.com API wrapper."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from supervisor.exceptions import PwnedSecret
from supervisor.utils import pwned
from supervisor.utils.pwned import check_pwned_password

PWNED_HASH = "5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8"
OTHER_HASH = "5BAA6FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
RANGE_RESPONSE = "1E4C9B93F3F0682250B6CF8331B7EE68FD8:3861493\r\n"


@pytest.fixture(autouse=True)
def clear_cache() -> Generator[None]:
    """Isolate the module-level pwned cache between tests."""
    with patch.object(pwned, "_CACHE", set()):
        yield


@pytest.fixture(name="websession")
def fixture_websession() -> MagicMock:
    """Mock aiohttp session returning a HIBP range response."""
    response = MagicMock(status=200)
    response.text = AsyncMock(return_value=RANGE_RESPONSE)
    websession = MagicMock()
    websession.get.return_value.__aenter__.return_value = response
    return websession


async def test_pwned_hash_cached(websession: MagicMock) -> None:
    """Test a pwned hash is cached and later checks skip the API."""
    with pytest.raises(PwnedSecret):
        await check_pwned_password(websession, PWNED_HASH.lower())
    assert websession.get.call_count == 1

    with pytest.raises(PwnedSecret):
        await check_pwned_password(websession, PWNED_HASH)
    assert websession.get.call_count == 1


async def test_cache_does_not_match_same_prefix(websession: MagicMock) -> None:
    """Test a different hash sharing the cached prefix is still checked."""
    with pytest.raises(PwnedSecret):
        await check_pwned_password(websession, PWNED_HASH)

    await check_pwned_password(websession, OTHER_HASH)
    assert websession.get.call_count == 2
