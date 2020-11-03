"""Testing handling with main."""
from pathlib import Path

import supervisor.__main__ as main


def test_write_state(tmp_path):
    """Test write corestate to /run/supervisor."""
    test_file = Path(tmp_path, "test.file")

    test_file.touch()
    assert test_file.exists()

    main.CONTAINER_OS_STARTUP_CHECK = test_file
    main.run_os_startup_check_cleanup()

    assert not test_file.exists()
