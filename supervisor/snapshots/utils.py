"""Util add-on functions."""
import hashlib
import re
import shutil

RE_DIGITS = re.compile(r"\d+")


def password_to_key(password):
    """Generate a AES Key from password."""
    password = password.encode()
    for _ in range(100):
        password = hashlib.sha256(password).digest()
    return password[:16]


def password_for_validating(password):
    """Generate a SHA256 hash from password."""
    for _ in range(100):
        password = hashlib.sha256(password.encode()).hexdigest()
    try:
        return str(sum(map(int, RE_DIGITS.findall(password))))[0]
    except (ValueError, IndexError):
        return "0"


def key_to_iv(key):
    """Generate an iv from Key."""
    for _ in range(100):
        key = hashlib.sha256(key).digest()
    return key[:16]


def create_slug(name, date_str):
    """Generate a hash from repository."""
    key = "{} - {}".format(date_str, name).lower().encode()
    return hashlib.sha1(key).hexdigest()[:8]


def remove_folder(folder):
    """Remove folder data but not the folder itself."""
    for obj in folder.iterdir():
        try:
            if obj.is_dir():
                shutil.rmtree(obj, ignore_errors=True)
            else:
                obj.unlink()
        except (OSError, shutil.Error):
            pass
