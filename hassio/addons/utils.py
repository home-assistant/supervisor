"""Util add-ons functions."""
import asyncio
import hashlib
import logging
import re

from ..const import (
    SECURITY_DISABLE, SECURITY_PROFILE, PRIVILEGED_NET_ADMIN,
    PRIVILEGED_SYS_ADMIN, PRIVILEGED_SYS_RAWIO, PRIVILEGED_SYS_PTRACE,
    PRIVILEGED_DAC_READ_SEARCH, ROLE_ADMIN, ROLE_MANAGER)

RE_SHA1 = re.compile(r"[a-f0-9]{8}")

_LOGGER = logging.getLogger(__name__)


def rating_security(addon):
    """Return 1-5 for security rating.

    1 = not secure
    5 = high secure
    """
    rating = 5

    # AppArmor
    if addon.apparmor == SECURITY_DISABLE:
        rating += -1
    elif addon.apparmor == SECURITY_PROFILE:
        rating += 1

    # Home Assistant Login
    if addon.access_auth_api:
        rating += 1

    # Privileged options
    if any(privilege in addon.privileged
           for privilege in (PRIVILEGED_NET_ADMIN, PRIVILEGED_SYS_ADMIN,
                             PRIVILEGED_SYS_RAWIO, PRIVILEGED_SYS_PTRACE,
                             PRIVILEGED_DAC_READ_SEARCH)):
        rating += -1

    # API Hass.io role
    if addon.hassio_role == ROLE_MANAGER:
        rating += -1
    elif addon.hassio_role == ROLE_ADMIN:
        rating += -2

    # Not secure Networking
    if addon.host_network:
        rating += -1

    # Insecure PID namespace
    if addon.host_pid:
        rating += -2

    # Full Access
    if addon.with_full_access:
        rating += -2

    # Docker Access
    if addon.access_docker_api:
        rating = 1

    return max(min(6, rating), 1)


def get_hash_from_repository(name):
    """Generate a hash from repository."""
    key = name.lower().encode()
    return hashlib.sha1(key).hexdigest()[:8]


def extract_hash_from_path(path):
    """Extract repo id from path."""
    repo_dir = path.parts[-1]

    if not RE_SHA1.match(repo_dir):
        return get_hash_from_repository(repo_dir)
    return repo_dir


def check_installed(method):
    """Wrap function with check if add-on is installed."""
    async def wrap_check(addon, *args, **kwargs):
        """Return False if not installed or the function."""
        if not addon.is_installed:
            _LOGGER.error("Addon %s is not installed", addon.slug)
            return False
        return await method(addon, *args, **kwargs)

    return wrap_check


async def remove_data(folder):
    """Remove folder and reset privileged."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "rm", "-rf", str(folder),
            stdout=asyncio.subprocess.DEVNULL
        )

        _, error_msg = await proc.communicate()
    except OSError as err:
        error_msg = str(err)

    if proc.returncode == 0:
        return
    _LOGGER.error("Can't remove Add-on Data: %s", error_msg)
