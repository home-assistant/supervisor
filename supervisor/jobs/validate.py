"""Validate services schema."""

import voluptuous as vol

from .const import ATTR_IGNORE_CONDITIONS, JobCondition

SCHEMA_JOBS_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_IGNORE_CONDITIONS, default=list): [vol.Coerce(JobCondition)],
    },
    extra=vol.REMOVE_EXTRA,
)
