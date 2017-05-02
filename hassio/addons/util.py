"""Util addons functions."""
import hashlib
import re

RE_SLUGIFY = re.compile(r'[^a-z0-9_]+')
RE_SHA1 = re.compile(r"[a-f0-9]{8}")


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


def create_hash_index_list(name_list):
    """Create a dict with hash from repositories list."""
    return {get_hash_from_repository(repo): repo for repo in name_list}
