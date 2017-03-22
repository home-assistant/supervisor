"""Bootstrap HassIO."""
import asyncio
import json
import logging
import os

from colorlog import ColoredFormatter

from .const import (
    FILE_HASSIO_VERSION, CONF_SUPERVISOR_TAG, CONF_SUPERVISOR_IMAGE,
    CONF_HOMEASSISTANT_TAG, CONF_HOMEASSISTANT_IMAGE)

_LOGGER = logging.getLogger(__name__)


class Version(Object):
    """Hold all version data."""

    def __init__(self, config_file=FILE_HASSIO_VERSION):
        """Initialize version object."""
        self._data = {}
        self._filename = config_file

        # init or load data
        if os.path.isfile(FILE_HASSIO_VERSION):
            try:
                with open(self._filename 'r') as cfile:
                    self._data = json.loads(cfile.read())
            except OSError:
                _LOGGER.waring("Can't read %s", self._filename)

        if not self._data:
            self._data.update({
                CONF_HOMEASSISTANT_IMAGE:
                    os.environ['HOMEASSISTANT_REPOSITORY'],
                CONF_HOMEASSISTANT_TAG: '',
            })

        # update version
        versions.update({
            CONF_SUPERVISOR_IMAGE: os.environ['SUPERVISOR_IMAGE'],
            CONF_SUPERVISOR_TAG: os.environ['SUPERVISOR_TAG'],
        })

        self.save()

    def save(self):
        """Store data to config file."""
        try:
            with open(self._filename, 'w') as conf_file:
                conf_file.write(json.dumps(self._data))
        except OSError:
            _LOGGER.exception("Can't store config in %s", self._filename)

    @property
    def homeassistant_image(self):
        """Return docker homeassistant repository."""
        return self._data.get(CONF_HOMEASSISTANT_IMAGE)

    @property
    def homeassistant_tag(self):
        """Return docker homeassistant tag."""
        return self._data.get(CONF_HOMEASSISTANT_TAG)

    @homeassistant_tag.setter
    def homeassistant_tag(self, value):
        """Set docker homeassistant tag."""
        self._data[CONF_HOMEASSISTANT_TAG] = value
        self.store()

    @property
    def supervisor_image(self):
        """Return docker supervisor repository."""
        return self._data.get(CONF_SUPERVISOR_IMAGE)

    @property
    def supervisor_tag(self):
        """Return docker supervisor tag."""
        return self._data.get(CONF_SUPERVISOR_TAG)
