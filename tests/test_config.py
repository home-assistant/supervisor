"""Test Supervisor core config."""

import json
from pathlib import Path

import pytest

from supervisor.config import CoreConfig
from supervisor.const import FeatureFlag


@pytest.mark.parametrize(
    ("existing", "expected"),
    [
        pytest.param(None, True, id="new-installation"),
        pytest.param({}, False, id="existing-installation"),
        pytest.param(
            {"feature_flags": {"app_drop_net_raw": False}},
            False,
            id="existing-installation-explicit",
        ),
    ],
)
async def test_new_installation_feature_flags(
    tmp_path: Path, existing: dict | None, expected: bool
):
    """Test security feature flags are only enabled by default on new installations."""
    config_file = tmp_path / "config.json"
    if existing is not None:
        config_file.write_text(json.dumps(existing))

    config = CoreConfig()
    config._file = config_file  # pylint: disable=protected-access
    await config.read_data()

    assert config.feature_flags.get(FeatureFlag.APP_DROP_NET_RAW, False) is expected
    assert (
        config.feature_flags.get(FeatureFlag.APP_REDUCED_CAPABILITIES, False)
        is expected
    )
