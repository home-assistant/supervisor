"""Some functions around apparmor profiles."""
import re

from ..exceptions import AppArmorFileError, AppArmorInvalidError

RE_PROFILE = re.compile(r"^profile ([^ ]+).*$")


def validate_profile(profile_file, profile_name):
    """Check if profile from file is valid with profile name."""
    profiles = set()

    try:
        with profile_file.open('r') as profile:
            for line in profile:
                match = RE_PROFILE.match(line)
                if not match:
                    continue
                profiles.add(match.group(1))
    except OSError as err:
        _LOGGER.error("Can't read apparmor profile: %s", err)
        raise AppArmorFileError()

    if len(profiles) != 1:
        _LOGGER.error("To many profiles inside file: %s", profiles)
        raise AppArmorInvalidError()

    if profile_name in profiles:
        return True
    return False
