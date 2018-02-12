"""Tarfile fileobject handler for encrypted files."""

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
        tar_mode = f"{mode}|gz" if gzip else f"{mode}|"
        
        # Extract IV for CBC
        if mode == MOD_READ:
            cbc_iv = self._file.read(16)
        else:
            cbc_iv = get_random_bytes(16)
            self._file.write(cbc_iv)

        self._aes = AES.new(key, AES.MODE_CBC, iv=cbc_iv)

    def write(self, data):
        """Write data."""
        if len(data) % BLOCK_SIZE != 0:
            data = pad(data, BLOCK_SIZE)
        self._file.write(self._aes.encrypt(data))

    def read(self, size=0):
        """Read data."""
        return self._aes.decrypt(self._file.read(size))

    def close(self):
        """Close file."""
        self._file.close()
