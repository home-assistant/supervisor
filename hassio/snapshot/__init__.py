"""Snapshot system control."""
import tarfile
from tempfile import TemporaryDirectory

from .tools import write_json_file, read_json_file


class SnapshotManager(object):
