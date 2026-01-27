"""Util add-on functions."""

import hashlib
import re

RE_DIGITS = re.compile(r"\d+")


def create_slug(name: str, date_str: str) -> str:
    """Generate a hash from repository."""
    key = f"{date_str} - {name}".lower().encode()
    return hashlib.sha1(key).hexdigest()[:8]
