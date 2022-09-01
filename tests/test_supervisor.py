"""Test supervisor object."""

from unittest.mock import AsyncMock, PropertyMock, patch

from aiohttp.client_exceptions import ClientError
import pytest

from supervisor.coresys import CoreSys


@pytest.fixture(name="websession")
async def fixture_webession(coresys: CoreSys):
    """Mock of websession."""
    mock_websession = AsyncMock()
    with patch.object(
        type(coresys), "websession", new=PropertyMock(return_value=mock_websession)
    ):
        yield mock_websession


@pytest.mark.parametrize(
    "side_effect,connectivity", [(ClientError(), False), (None, True)]
)
async def test_connectivity_check(
    coresys: CoreSys,
    websession: AsyncMock,
    side_effect: Exception | None,
    connectivity: bool,
):
    """Test connectivity check."""
    assert coresys.supervisor.connectivity is True

    websession.head.side_effect = side_effect
    await coresys.supervisor.check_connectivity()

    assert coresys.supervisor.connectivity is connectivity


@pytest.mark.parametrize("side_effect,call_count", [(ClientError(), 3), (None, 1)])
async def test_connectivity_check_throttling(
    coresys: CoreSys,
    websession: AsyncMock,
    side_effect: Exception | None,
    call_count: int,
):
    """Test connectivity check throttled when checks succeed."""
    websession.head.side_effect = side_effect

    for _ in range(3):
        await coresys.supervisor.check_connectivity()

    assert websession.head.call_count == call_count
