"""Tarfile fileobject handler for encrypted files."""
import hashlib
import os
from pathlib import Path
import tarfile
from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import ciphers, padding

BLOCK_SIZE = 16

MOD_READ = "r"
MOD_WRITE = "w"


class SecureTarFile:
    """Handle encrypted files for tarfile library."""

    def __init__(
        self, name: Path, mode: str, key: Optional[bytes] = None, gzip: bool = True
    ):
        """Initialize encryption handler."""
        self._file = None
        self._mode: str = mode
        self._name: Path = name

        # Tarfile options
        self._tar = None
        self._tar_mode = f"{mode}|gz" if gzip else f"{mode}|"

        # Encryption/Decription
        self._aes: Optional[ciphers.Cipher] = None
        self._key: bytes = key

        # Function helper
        self._decrypt: Optional[ciphers.CipherContext] = None
        self._encrypt: Optional[ciphers.CipherContext] = None

    def __enter__(self):
        """Start context manager tarfile."""
        if not self._key:
            self._tar = tarfile.open(name=str(self._name), mode=self._tar_mode)
            return self._tar

        # Encrypted/Decryped Tarfile
        self._file = self._name.open(f"{self._mode}b")

        # Extract IV for CBC
        if self._mode == MOD_READ:
            cbc_rand = self._file.read(16)
        else:
            cbc_rand = os.urandom(16)
            self._file.write(cbc_rand)

        # Create Cipher
        self._aes = ciphers.Cipher(
            ciphers.algorithms.AES(self._key),
            ciphers.modes.CBC(_generate_iv(self._key, cbc_rand)),
            backend=default_backend(),
        )

        self._decrypt = self._aes.decryptor()
        self._encrypt = self._aes.encryptor()

        self._tar = tarfile.open(fileobj=self, mode=self._tar_mode)
        return self._tar

    def __exit__(self, exc_type, exc_value, traceback):
        """Close file."""
        if self._tar:
            self._tar.close()
        if self._file:
            self._file.close()

    def write(self, data: bytes):
        """Write data."""
        if len(data) % BLOCK_SIZE != 0:
            padder = padding.PKCS7(BLOCK_SIZE).padder()
            data = padder.update(data) + padder.finalize()

        self._file.write(self._encrypt.update(data))

    def read(self, size: int = 0):
        """Read data."""
        return self._decrypt.update(self._file.read(size))

    @property
    def path(self):
        """Return path object of tarfile."""
        return self._name

    @property
    def size(self):
        """Return snapshot size."""
        if not self._name.is_file():
            return 0
        return round(self._name.stat().st_size / 1_048_576, 2)  # calc mbyte


def _generate_iv(key: bytes, salt: bytes):
    """Generate an iv from data."""
    temp_iv = key + salt
    for _ in range(100):
        temp_iv = hashlib.sha256(temp_iv).digest()
    return temp_iv[:16]
