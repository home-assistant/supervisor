"""Handle Home Assistant secrets to add-ons."""
from datetime import timedelta
import logging
from pathlib import Path
from typing import Dict, Optional, Union

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import YamlFileError
from ..jobs.const import JobExecutionLimit
from ..jobs.decorator import Job
from ..utils.yaml import read_yaml_file

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HomeAssistantSecrets(CoreSysAttributes):
    """Manage Home Assistant secrets."""

    def __init__(self, coresys: CoreSys):
        """Initialize secret manager."""
        self.coresys: CoreSys = coresys
        self.secrets: Dict[str, Union[bool, float, int, str]] = {}

    @property
    def path_secrets(self) -> Path:
        """Return path to secret file."""
        return Path(self.sys_config.path_homeassistant, "secrets.yaml")

    def get(self, secret: str) -> Optional[Union[bool, float, int, str]]:
        """Get secret from store."""
        _LOGGER.info("Request secret %s", secret)
        return self.secrets.get(secret)

    async def load(self) -> None:
        """Load secrets on start."""
        await self._read_secrets()

        _LOGGER.info("Loaded %s Home Assistant secrets", len(self.secrets))

    async def reload(self) -> None:
        """Reload secrets."""
        await self._read_secrets()

    @Job(limit=JobExecutionLimit.THROTTLE_WAIT, throttle_period=timedelta(seconds=60))
    async def _read_secrets(self):
        """Read secrets.yaml into memory."""
        if not self.path_secrets.exists():
            _LOGGER.debug("Home Assistant secrets not exists")
            return

        # Read secrets
        try:
            secrets = await self.sys_run_in_executor(read_yaml_file, self.path_secrets)
        except YamlFileError as err:
            _LOGGER.warning("Can't read Home Assistant secrets: %s", err)
            return

        if not isinstance(secrets, dict):
            return

        # Process secrets
        self.secrets = {
            k: v for k, v in secrets.items() if isinstance(v, (bool, float, int, str))
        }
        _LOGGER.debug("Reloading Home Assistant secrets: %s", len(self.secrets))
