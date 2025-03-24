"""Tests for apparmor utility."""

from pathlib import Path

import pytest

from supervisor.exceptions import AppArmorInvalidError
from supervisor.utils.apparmor import adjust_profile, validate_profile

from tests.common import get_fixture_path

TEST_PROFILE = """
#include <tunables/global>

profile test flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  # Capabilities
  file,
  signal (send) set=(kill,term,int,hup,cont),

  # Start new profile for service
  /usr/bin/my_program cx -> my_program,

  profile my_program flags=(attach_disconnected,mediate_deleted) {
    #include <abstractions/base>
  }
}
""".strip()


async def test_valid_apparmor_file():
    """Test a valid apparmor file."""
    assert validate_profile("example", get_fixture_path("apparmor_valid.txt"))


async def test_apparmor_missing_profile(caplog: pytest.LogCaptureFixture):
    """Test apparmor file missing profile."""
    with pytest.raises(AppArmorInvalidError):
        validate_profile("example", get_fixture_path("apparmor_no_profile.txt"))

    assert (
        "Missing AppArmor profile inside file: apparmor_no_profile.txt" in caplog.text
    )


async def test_apparmor_multiple_profiles(caplog: pytest.LogCaptureFixture):
    """Test apparmor file with too many profiles."""
    with pytest.raises(AppArmorInvalidError):
        validate_profile("example", get_fixture_path("apparmor_multiple_profiles.txt"))

    assert (
        "Too many AppArmor profiles inside file: apparmor_multiple_profiles.txt"
        in caplog.text
    )


def test_apparmor_profile_adjust(tmp_path: Path):
    """Test apparmor profile adjust."""
    profile_out = tmp_path / "apparmor_out.txt"
    adjust_profile("test", get_fixture_path("apparmor_valid.txt"), profile_out)

    assert profile_out.read_text(encoding="utf-8") == TEST_PROFILE


def test_apparmor_profile_adjust_mediate(tmp_path: Path):
    """Test apparmor profile adjust when name matches a flag."""
    profile_out = tmp_path / "apparmor_out.txt"
    adjust_profile("test", get_fixture_path("apparmor_valid_mediate.txt"), profile_out)

    assert profile_out.read_text(encoding="utf-8") == TEST_PROFILE
