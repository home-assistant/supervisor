"""Test CodeNotary."""

import pytest

from supervisor.exceptions import CodeNotaryUntrusted
from supervisor.utils.codenotary import calc_checksum, cas_validate


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
