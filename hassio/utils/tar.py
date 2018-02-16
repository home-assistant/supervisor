"""Tarfile fileobject handler for encrypted files."""
import tarfile

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

BLOCK_SIZE = 16

MOD_READ = 'r'
MOD_WRITE = 'w'


class SecureTarFile(object):
    """Handle encrypted files for tarfile library."""

    def __init__(self, name, mode, key=None, gzip=True):
        """Initialize encryption handler."""
        self._file = None
        self._mode = mode
        self._name = name

        # Tarfile options
        self._tar = None
        self._tar_mode = f"{mode}|gz" if gzip else f"{mode}|"

        # Encryption/Decription
        self._aes = None
        self._key = key

    def __enter__(self):
        """Start context manager tarfile."""
        if not self._key:
            self._tar = tarfile.open(name=str(self._name), mode=self._tar_mode)
            return self._tar

        # Encrypted/Decryped Tarfile
        self._file = self._name.open(self._mode)

        # Extract IV for CBC
        if self._mode == MOD_READ:
            cbc_iv = self._file.read(16)
        else:
            cbc_iv = get_random_bytes(16)
            self._file.write(cbc_iv)
        self._aes = AES.new(self._key, AES.MODE_CBC, iv=cbc_iv)

        self._tar = tarfile.open(fileobj=self, mode=self._tar_mode)
        return self._tar

    def __exit__(self, exc_type, exc_value, traceback):
        """Close file."""
        if self._tar:
            self._tar.close()
        if self._file:
            self._file.close()

    def write(self, data):
        """Write data."""
        if len(data) % BLOCK_SIZE != 0:
            data = pad(data, BLOCK_SIZE)
        self._file.write(self._aes.encrypt(data))

    def read(self, size=0):
        """Read data."""
        return self._aes.decrypt(self._file.read(size))

    @property
    def path(self):
        """Return path object of tarfile."""
        return self._name

    @property
    def size(self):
        """Return snapshot size."""
        if not self._name.is_file():
            return 0
        return round(self._name.stat().st_size / 1048576)  # calc mbyte
