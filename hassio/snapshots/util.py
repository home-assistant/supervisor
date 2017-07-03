"""Util addons functions."""
import hashlib


def create_slug(name, date_str):
    """Generate a hash from repository."""
    key = "{} - {}".format(date_str, name).lower().encode()
    return hashlib.sha1(key).hexdigest()[:8]
