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

pytest.skip("code notary has been disabled due to issues", allow_module_level=True)


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
        communicate_return = AsyncMock(return_value=(response.data, response.error))

    exec_return = Mock(returncode=response.returncode, communicate=communicate_return)

    with patch(
        "supervisor.utils.codenotary.asyncio.create_subprocess_exec",
        return_value=exec_return,
    ) as subprocess_exec:
        yield subprocess_exec


def test_checksum_calc():
    """Calc Checkusm as test."""
    assert calc_checksum("test") == calc_checksum(b"test")
    assert (
        calc_checksum("test")
        == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    )


async def test_valid_checksum():
    """Test a valid autorization."""
    await cas_validate(
        "notary@home-assistant.io",
        "4434a33ff9c695e870bc5bbe04230ea3361ecf4c129eb06133dd1373975a43f0",
    )


async def test_invalid_checksum():
    """Test a invalid autorization."""
    with pytest.raises(CodeNotaryUntrusted):
        await cas_validate(
            "notary@home-assistant.io",
            "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        )


@pytest.mark.parametrize(
    "subprocess_exec",
    [SubprocessResponse(returncode=1, error=b"x is not notarized")],
)
async def test_not_notarized_error(subprocess_exec):
    """Test received a not notarized error response from command."""
    with pytest.raises(CodeNotaryUntrusted):
        await cas_validate(
            "notary@home-assistant.io",
            "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        )


@pytest.mark.parametrize(
    "subprocess_exec",
    [
        SubprocessResponse(returncode=1, error=b"test"),
        SubprocessResponse(returncode=0, data='{"error":"asn1: structure error"}'),
        SubprocessResponse(returncode=1, error="test".encode("utf-16")),
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
