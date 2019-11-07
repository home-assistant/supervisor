"""Tarfile fileobject handler for encrypted files."""
import hashlib
import logging
import os
from pathlib import Path
import tarfile
from typing import IO, Callable, Generator, List, Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import (
    Cipher,
    CipherContext,
    algorithms,
    modes,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

BLOCK_SIZE = 16
BLOCK_SIZE_BITS = 128

MOD_READ = "r"
MOD_WRITE = "w"


class SecureTarFile:
    """Handle encrypted files for tarfile library."""

    def __init__(
        self, name: Path, mode: str, key: Optional[bytes] = None, gzip: bool = True
    ) -> None:
        """Initialize encryption handler."""
        self._file: Optional[IO[bytes]] = None
        self._mode: str = mode
        self._name: Path = name

        # Tarfile options
        self._tar: Optional[tarfile.TarFile] = None
        self._tar_mode: str = f"{mode}|gz" if gzip else f"{mode}|"

        # Encryption/Description
        self._aes: Optional[Cipher] = None
        self._key: bytes = key

        # Function helper
        self._decrypt: Optional[CipherContext] = None
        self._encrypt: Optional[CipherContext] = None

    def __enter__(self) -> tarfile.TarFile:
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
        self._aes = Cipher(
            algorithms.AES(self._key),
            modes.CBC(_generate_iv(self._key, cbc_rand)),
            backend=default_backend(),
        )

        self._decrypt = self._aes.decryptor()
        self._encrypt = self._aes.encryptor()

        self._tar = tarfile.open(fileobj=self, mode=self._tar_mode)
        return self._tar

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Close file."""
        if self._tar:
            self._tar.close()
        if self._file:
            self._file.close()

    def write(self, data: bytes) -> None:
        """Write data."""
        if len(data) % BLOCK_SIZE != 0:
            padder = padding.PKCS7(BLOCK_SIZE_BITS).padder()
            data = padder.update(data) + padder.finalize()

        self._file.write(self._encrypt.update(data))

    def read(self, size: int = 0) -> bytes:
        """Read data."""
        return self._decrypt.update(self._file.read(size))

    @property
    def path(self) -> Path:
        """Return path object of tarfile."""
        return self._name

    @property
    def size(self) -> int:
        """Return snapshot size."""
        if not self._name.is_file():
            return 0
        return round(self._name.stat().st_size / 1_048_576, 2)  # calc mbyte


def _generate_iv(key: bytes, salt: bytes) -> bytes:
    """Generate an iv from data."""
    temp_iv = key + salt
    for _ in range(100):
        temp_iv = hashlib.sha256(temp_iv).digest()
    return temp_iv[:16]


def secure_path(tar: tarfile.TarFile) -> Generator[tarfile.TarInfo, None, None]:
    """Security safe check of path.

    Prevent ../ or absolut paths
    """
    for member in tar:
        file_path = Path(member.name)
        try:
            assert not file_path.is_absolute()
            Path("/fake", file_path).resolve().relative_to("/fake")
        except (ValueError, RuntimeError, AssertionError):
            _LOGGER.warning("Issue with file %s", file_path)
            continue
        else:
            yield member


def exclude_filter(
    exclude_list: List[str],
) -> Callable[[tarfile.TarInfo], Optional[tarfile.TarInfo]]:
    """Create callable filter function to check TarInfo for add."""

    def my_filter(tar: tarfile.TarInfo) -> Optional[tarfile.TarInfo]:
        """Custom exclude filter."""
        file_path = Path(tar.name)
        for exclude in exclude_list:
            if not file_path.match(exclude):
                continue
            _LOGGER.debug("Ignore %s because of %s", file_path, exclude)
            return None

        return tar

    return my_filter
