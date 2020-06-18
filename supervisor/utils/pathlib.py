"""Pathlib utility for exclusion filtering."""
import logging
from pathlib import PurePath
from typing import List

_LOGGER: logging.Logger = logging.getLogger(__name__)


def is_excluded_by_filter(path: PurePath, exclude_list: List[str]) -> bool:
    """Filter to filter excludes."""

    for exclude in exclude_list:
        if not path.match(exclude):
            continue
        _LOGGER.debug("Ignore %s because of %s", path, exclude)
        return True

    return False
