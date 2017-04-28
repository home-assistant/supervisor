"""Util addons functions."""
import hashlib
import pathlib
import re

RE_SLUGIFY = re.compile(r'[^a-z0-9_]+')
RE_SHA1 = re.compile(r"[a-f0-9]{8}")


def get_hash_from_repository(repo):
    """Generate a hash from repository."""
    key = repo.lower().encode()
    return hashlib.sha1(key).hexdigest()[:8]


def extract_hash_from_path(base_path, options_path):
    """Extract repo id from path."""
    base_dir = pathlib.PurePosixPath(base_path).parts[-1]

    dirlist = iter(pathlib.PurePosixPath(options_path).parts)
    for obj in dirlist:
        if obj != base_dir:
            continue

        repo_dir = next(dirlist)
        if not RE_SHA1.match(repo_dir):
            return get_hash_from_repository(repo_dir)
        return repo_dir
