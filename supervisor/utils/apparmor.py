"""Some functions around AppArmor profiles."""

import logging
from pathlib import Path
import re

from ..exceptions import AppArmorFileError, AppArmorInvalidError

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_PROFILE = re.compile(r"^profile ([^ ]+).*$")


def get_profile_name(profile_file: Path) -> str:
    """Read the profile name from file.

    Must be run in executor.
    """
    profiles = set()

    try:
        with profile_file.open("r") as profile_data:
            for line in profile_data:
                match = RE_PROFILE.match(line)
                if not match:
                    continue
                profiles.add(match.group(1))
    except OSError as err:
        raise AppArmorFileError(
            f"Can't read AppArmor profile: {err}", _LOGGER.error
        ) from err

    if len(profiles) == 0:
        raise AppArmorInvalidError(
            f"Missing AppArmor profile inside file: {profile_file.name}", _LOGGER.error
        )

    if len(profiles) != 1:
        raise AppArmorInvalidError(
            f"Too many AppArmor profiles inside file: {profile_file.name}",
            _LOGGER.error,
        )

    return profiles.pop()


def validate_profile(profile_name: str, profile_file: Path) -> bool:
    """Check if profile from file is valid with profile name.

    Must be run in executor.
    """
    if profile_name == get_profile_name(profile_file):
        return True
    return False


def adjust_profile(profile_name: str, profile_file: Path, profile_new: Path) -> None:
    """Fix the profile name.

    Must be run in executor.
    """
    org_profile = get_profile_name(profile_file)
    profile_data = []

    # Process old data
    try:
        with profile_file.open("r") as profile:
            for line in profile:
                match = RE_PROFILE.match(line)
                if not match:
                    profile_data.append(line)
                else:
                    profile_data.append(line.replace(org_profile, profile_name, 1))
    except OSError as err:
        raise AppArmorFileError(
            f"Can't adjust origin profile: {err}", _LOGGER.error
        ) from err

    # Write into new file
    try:
        with profile_new.open("w") as profile:
            profile.writelines(profile_data)
    except OSError as err:
        raise AppArmorFileError(
            f"Can't write new profile: {err}", _LOGGER.error
        ) from err
