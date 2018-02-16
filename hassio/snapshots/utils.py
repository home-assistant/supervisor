"""Util addons functions."""
import hashlib
import shutil


def password_to_key(password):
    """Generate a AES Key from password"""
    password = password.encode()
    for _ in range(100):
        password = hashlib.sha256(password).digest()
    return password[:16]


def password_for_validating(password):
    """Generate a SHA256 hash from password"""
    for _ in range(100):
        password = hashlib.sha256(password.encode()).hexdigest()
    return password


def create_slug(name, date_str):
    """Generate a hash from repository."""
    key = "{} - {}".format(date_str, name).lower().encode()
    return hashlib.sha1(key).hexdigest()[:8]


def remove_folder(folder):
    """Remove folder data but not the folder itself."""
    for obj in folder.iterdir():
        try:
            if obj.is_dir():
                shutil.rmtree(str(obj), ignore_errors=True)
            else:
                obj.unlink()
        except (OSError, shutil.Error):
            pass
