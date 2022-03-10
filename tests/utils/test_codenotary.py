"""Test CodeNotary."""
from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock, Mock, patch

import pytest

from supervisor.exceptions import (
    CodeNotaryBackendError,
    CodeNotaryError,
    CodeNotaryUntrusted,
)
from supervisor.utils.codenotary import calc_checksum, cas_validate


@dataclass
class SubprocessResponse:
    """Class for specifying subprocess exec response."""

    returncode: int = 0
    data: str = ""
    error: str | None = None
    exception: Exception | None = None


@pytest.fixture(name="subprocess_exec")
def fixture_subprocess_exec(request):
    """Mock subprocess exec with specific return."""
    response = request.param
    if response.exception:
        communicate_return = AsyncMock(side_effect=response.exception)
    else:
        err_return = None
        if response.error:
            err_return = Mock(decode=Mock(return_value=response.error))

        communicate_return = AsyncMock(return_value=(response.data, err_return))

    exec_return = Mock(returncode=response.returncode, communicate=communicate_return)

    with patch(
        "supervisor.utils.codenotary.asyncio.create_subprocess_exec",
        return_value=exec_return,
    ) as subprocess_exec:
        yield subprocess_exec


@pytest.mark.skip()
def test_checksum_calc():
    """Calc Checkusm as test."""
    assert calc_checksum("test") == calc_checksum(b"test")
    assert (
        calc_checksum("test")
        == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    )


@pytest.mark.skip()
async def test_valid_checksum():
    """Test a valid autorization."""
    await cas_validate(
        "notary@home-assistant.io",
        "4434a33ff9c695e870bc5bbe04230ea3361ecf4c129eb06133dd1373975a43f0",
    )


@pytest.mark.skip()
async def test_invalid_checksum():
    """Test a invalid autorization."""
    with pytest.raises(CodeNotaryUntrusted):
        await cas_validate(
            "notary@home-assistant.io",
            "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        )


@pytest.mark.skip()
@pytest.mark.parametrize(
    "subprocess_exec",
    [
        SubprocessResponse(returncode=1, error="test"),
        SubprocessResponse(returncode=0, data='{"error":"asn1: structure error"}'),
    ],
    indirect=True,
)
async def test_cas_backend_error(subprocess_exec):
    """Test backend error executing cas command."""
    with pytest.raises(CodeNotaryBackendError):
        await cas_validate(
            "notary@home-assistant.io",
            "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        )


@pytest.mark.skip()
@pytest.mark.parametrize(
    "subprocess_exec",
    [SubprocessResponse(returncode=0, data='{"status":1}')],
    indirect=True,
)
async def test_cas_notarized_untrusted(subprocess_exec):
    """Test cas found notarized but untrusted content."""
    with pytest.raises(CodeNotaryUntrusted):
        await cas_validate(
            "notary@home-assistant.io",
            "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        )


@pytest.mark.skip()
@pytest.mark.parametrize(
    "subprocess_exec", [SubprocessResponse(exception=OSError())], indirect=True
)
async def test_cas_exec_os_error(subprocess_exec):
    """Test os error attempting to execute cas command."""
    with pytest.raises(CodeNotaryError):
        await cas_validate(
            "notary@home-assistant.io",
            "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        )
