"""Util addons functions."""
import hashlib
import pathlib
import re
import unicodedata

RE_SLUGIFY = re.compile(r'[^a-z0-9_]+')


def slugify(text):
    """Slugify a given text."""
    text = unicodedata.normalize('NFKD', text)
    text = text.lower()
    text = text.replace(" ", "_")
    text = RE_SLUGIFY.sub("", text)

    return text


def get_hash_from_repository(repo):
    """Generate a hash from repository."""
    key = repo.lower().encode()
    return hashlib.sha1(key).hexdigest()


def extract_hash_from_path(base_path, options_path):
    """Extract repo id from path."""
    base_dir = pathlib.PurePosixPath(base_path).parts[-1]

    dirlist = iter(pathlib.PurePosixPath(options_path).parts)
    for obj in dirlist:
        if obj != base_dir:
            continue
        return slugify(next(dirlist))
