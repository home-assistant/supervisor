"""Test CodeNotary."""


from supervisor.utils.codenotary import calc_checksum


def test_checksum_calc():
    """Calc Checkusm as test."""
    assert calc_checksum("test") == calc_checksum(b"test")
    assert (
        calc_checksum("test")
        == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    )
