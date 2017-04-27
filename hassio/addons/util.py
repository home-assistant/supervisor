"""Util addons functions."""
import hashlib


def get_hash_from_repository(repo):
    """Generate a hash from repository."""
    key = repo.lower().encode()
    return hashlib.sha1(key).hexdigest()
