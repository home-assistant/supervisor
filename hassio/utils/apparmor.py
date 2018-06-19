"""Some functions around apparmor profiles."""
import logging
import re

from ..exceptions import AppArmorFileError, AppArmorInvalidError

_LOGGER = logging.getLogger(__name__)

RE_PROFILE = re.compile(r"^profile ([^ ]+).*$")

def get_profile_name(profile_file):
    """Read the profile name from file."""
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

    return profiles[0]


def validate_profile(profile_file, profile_name):
    """Check if profile from file is valid with profile name."""
    if profile_name == get_profile_name(profile_file):
        return True
    return False


def adjust_profile(profile_file, profile_name, profile_new):
    """Fix the profile name."""
    org_profile = get_profile_name(profile_file)
    profile_data = []
    
    try:
        with profile_file.open('r') as profile:
            for line in profile:
                match = RE_PROFILE.match(line)
                if not match:
                    profile_data.append(line)
                    continue
                
    except OSError as err:
        _LOGGER.error("Can't adjust origin profile: %s", err)
        raise AppArmorFileError()
