"""Util add-on functions."""
import hashlib
import re

RE_DIGITS = re.compile(r"\d+")


def password_to_key(password):
    """Generate a AES Key from password."""
    password = password.encode()
    for _ in range(100):
        password = hashlib.sha256(password).digest()
    return password[:16]


def key_to_iv(key):
    """Generate an iv from Key."""
    for _ in range(100):
        key = hashlib.sha256(key).digest()
    return key[:16]


def create_slug(name, date_str):
    """Generate a hash from repository."""
    key = f"{date_str} - {name}".lower().encode()
    return hashlib.sha1(key).hexdigest()[:8]
