"""Util add-ons functions."""
import hashlib
import logging
from pathlib import Path
import re

RE_SHA1 = re.compile(r"[a-f0-9]{8}")
_LOGGER: logging.Logger = logging.getLogger(__name__)


def get_hash_from_repository(name: str) -> str:
    """Generate a hash from repository."""
    key = name.lower().encode()
    return hashlib.sha1(key).hexdigest()[:8]


def extract_hash_from_path(path: Path) -> str:
    """Extract repo id from path."""
    repository_dir = path.parts[-1]

    if not RE_SHA1.match(repository_dir):
        return get_hash_from_repository(repository_dir)
    return repository_dir
