"""Test that we are reading add-on files correctly."""
from pathlib import Path
from unittest.mock import patch

from supervisor.coresys import CoreSys


async def test_read_addon_files(coresys: CoreSys):
    """Test that we are reading add-on files correctly."""
    with patch(
        "pathlib.Path.glob",
        return_value=[
            Path("addon/config.yml"),
            Path(".git/config.yml"),
            Path("somepath/.git/config.yml"),
            Path("somepath/deeper_in_the_structure/.github/config.yml"),
            Path(".github/config.yml"),
            Path("some/rootfs/config.yml"),
            Path(".circleci/config.yml"),
        ],
    ):
        addon_list = await coresys.store.data._find_addons(Path("test"), {})

        assert len(addon_list) == 1
        assert str(addon_list[0]) == "addon/config.yml"
