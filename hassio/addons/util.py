"""Util addons functions."""
import hashlib
import logging
import re

RE_SHA1 = re.compile(r"[a-f0-9]{8}")

_LOGGER = logging.getLogger(__name__)


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
    """Wrap function with check if addon is installed."""
    async def wrap_check(addon, *args, **kwargs):
        """Return False if not installed or the function."""
        if not addon.is_installed:
            _LOGGER.error("Addon %s is not installed", addon.slug)
            return False
        return await method(addon, *args, **kwargs)

    return wrap_check
