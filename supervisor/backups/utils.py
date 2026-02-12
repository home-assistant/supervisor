"""Util add-on functions."""

import hashlib
import logging
import re
import tarfile

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_DIGITS = re.compile(r"\d+")


def create_slug(name: str, date_str: str) -> str:
    """Generate a hash from repository."""
    key = f"{date_str} - {name}".lower().encode()
    return hashlib.sha1(key).hexdigest()[:8]


def backup_data_filter(
    member: tarfile.TarInfo, dest_path: str
) -> tarfile.TarInfo | None:
    """Filter for backup tar extraction.

    Applies tarfile.data_filter for security (rejects dangerous symlinks,
    device nodes, resets uid/gid) but skips problematic entries with a
    warning instead of aborting the entire extraction.
    """
    try:
        return tarfile.data_filter(member, dest_path)
    except tarfile.FilterError as err:
        _LOGGER.warning("Skipping %s: %s", member.name, err)
        return None
