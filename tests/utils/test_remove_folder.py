"""test json."""
from pathlib import Path
import shutil

import pytest

from supervisor.utils import remove_folder


@pytest.mark.asyncio
async def test_remove_all(tmp_path):
    """Test remove folder."""
    # Prepair test folder
    temp_orig = tmp_path.joinpath("orig")
    fixture_data = Path(__file__).parents[1].joinpath("fixtures/tar_data")
    shutil.copytree(fixture_data, temp_orig, symlinks=True)

    assert temp_orig.exists()
    await remove_folder(temp_orig)
    assert not temp_orig.exists()


@pytest.mark.asyncio
async def test_remove_content(tmp_path):
    """Test remove content of folder."""
    # Prepair test folder
    temp_orig = tmp_path.joinpath("orig")
    fixture_data = Path(__file__).parents[1].joinpath("fixtures/tar_data")
    shutil.copytree(fixture_data, temp_orig, symlinks=True)

    test_folder = Path(temp_orig, "test1")
    test_file = Path(temp_orig, "README.md")
    test_hidden = Path(temp_orig, ".hidden")

    test_hidden.touch()

    assert test_folder.exists()
    assert test_file.exists()
    assert test_hidden.exists()

    await remove_folder(temp_orig, content_only=True)

    assert not test_folder.exists()
    assert not test_file.exists()
    assert not test_hidden.exists()
