"""Unit tests for the utils function."""

import os
from pathlib import Path
import tempfile

from supervisor.utils import get_latest_mtime  # Adjust the import as needed


def test_get_latest_mtime_with_files():
    """Test the latest mtime with files in the directory."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)

        # Set an old mtime for the directory itself
        dir_mtime_initial = 1000000000

        # Create first file
        file1 = tmpdir / "file1.txt"
        file1.write_text("First file")
        # After creating file1, directory mtime was modified.
        os.utime(tmpdir, (dir_mtime_initial, dir_mtime_initial))

        file1_mtime = 1000000100
        os.utime(file1, (file1_mtime, file1_mtime))

        # Reset directory mtime back to older so that file1 is correctly detected
        os.utime(tmpdir, (dir_mtime_initial, dir_mtime_initial))

        # Verify file1 is detected
        latest_mtime1, latest_path1 = get_latest_mtime(tmpdir)
        assert latest_path1 == file1
        assert latest_mtime1 == file1_mtime

        # Create second file
        file2 = tmpdir / "file2.txt"
        file2.write_text("Second file")

        # Verify change is detected
        # Often the directory itself is the latest modified file
        # because a new file was created in it. But this is not
        # guaranteed, and also not relevant for the test.
        latest_mtime2, _ = get_latest_mtime(tmpdir)
        assert latest_mtime2 > latest_mtime1


def test_get_latest_mtime_directory_when_empty():
    """Test the latest mtime when the directory cleared."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)

        # Set initial mtime for the directory
        dir_mtime_initial = 1000000000

        # Create a file
        file1 = tmpdir / "file1.txt"
        file1.write_text("Temporary file")
        file1_mtime = 1000000100
        # After creating file1, directory mtime was modified.
        os.utime(tmpdir, (dir_mtime_initial, dir_mtime_initial))
        os.utime(file1, (file1_mtime, file1_mtime))

        # Verify the file is the latest
        latest_mtime1, latest_path = get_latest_mtime(tmpdir)
        assert latest_path == file1
        assert latest_mtime1 == file1_mtime

        # Now delete the file
        file1.unlink()

        # Now the directory itself should be the latest
        latest_mtime2, latest_path = get_latest_mtime(tmpdir)
        assert latest_path == tmpdir
        assert latest_mtime2 > latest_mtime1


def test_get_latest_mtime_empty_directory():
    """Test the latest mtime when the directory is empty."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)

        # Directory is empty
        latest_mtime, latest_path = get_latest_mtime(tmpdir)
        assert latest_path == tmpdir
        assert latest_mtime > 0
