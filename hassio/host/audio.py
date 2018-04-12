"""Host Audio-support."""
from collections import namedtuple
import logging
import json
from pathlib import Path
from string import Template

from ..const import (
    ATTR_CACHE, ATTR_INPUT, ATTR_OUTPUT, ATTR_DEVICES, ATTR_NAME, ATTR_DEFAULT)
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)

DefaultConfig = namedtuple('DefaultConfig', ['input', 'output'])


class AlsaAudio(CoreSysAttributes):
    """Handle Audio ALSA host data."""

    def __init__(self, coresys):
        """Initialize Alsa audio system."""
        self.coresys = coresys
        self._data = {
            ATTR_CACHE: 0,
            ATTR_INPUT: {},
            ATTR_OUTPUT: {},
        }

    @property
    def input_devices(self):
        """Return list of ALSA input devices."""
        self._update_device()
        return self._data[ATTR_INPUT]

    @property
    def output_devices(self):
        """Return list of ALSA output devices."""
        self._update_device()
        return self._data[ATTR_OUTPUT]

    def _update_device(self):
        """Update Internal device DB."""
        current_id = hash(frozenset(self._hardware.audio_devices))

        # Need rebuild?
        if current_id == self._data[ATTR_CACHE]:
            return

        # Init database
        _LOGGER.info("Update ALSA device list")
        database = self._audio_database()

        # Process devices
        for dev_id, dev_data in self._hardware.audio_devices.items():
            for chan_id, chan_type in dev_data[ATTR_DEVICES]:
                alsa_id = f"{dev_id},{chan_id}"
                if chan_type.endswith('playback'):
                    key = ATTR_OUTPUT
                elif chan_type.endswith('capture'):
                    key = ATTR_INPUT
                else:
                    _LOGGER.warning("Unknown channel type: %s", chan_type)
                    continue

                self._data[key][alsa_id] = database.get(self._machine, {}).get(
                    alsa_id, f"{dev_data[ATTR_NAME]}: {chan_id}")

        self._data[ATTR_CACHE] = current_id

    @staticmethod
    def _audio_database():
        """Read local json audio data into dict."""
        json_file = Path(__file__).parent.joinpath('audiodb.json')

        try:
            with json_file.open('r') as database:
                return json.loads(database.read())
        except (ValueError, OSError) as err:
            _LOGGER.warning("Can't read audio DB: %s", err)

        return {}

    @property
    def default(self):
        """Generate ALSA default setting."""
        if ATTR_DEFAULT in self._data:
            default = self._data[ATTR_DEFAULT]
        else:
            default = None

        # Init defaults
        if default is None:
            database = self._audio_database()
            alsa_input = database.get(self._machine, {}).get(ATTR_INPUT)
            alsa_output = database.get(self._machine, {}).get(ATTR_OUTPUT)

            default = self._data[ATTR_DEFAULT] = \
                DefaultConfig(alsa_input, alsa_output)

        # Search exists/new output
        if default.output is None and self.output_devices:
            default.output = next(iter(self.output_devices))
            _LOGGER.info("Detect output device %s", default.output)

        # Search exists/new input
        if default.input is None and self.input_devices:
            default.input = next(iter(self.input_devices))
            _LOGGER.info("Detect input device %s", default.input)

        return default

    def asound(self, alsa_input=None, alsa_output=None):
        """Generate a asound data."""
        alsa_input = alsa_input or self.default.input
        alsa_output = alsa_output or self.default.output

        # Read Template
        asound_file = Path(__file__).parent.joinpath('asound.tmpl')
        try:
            with asound_file.open('r') as asound:
                asound_data = asound.read()
        except OSError as err:
            _LOGGER.error("Can't read asound.tmpl: %s", err)
            return ""

        # Process Template
        asound_template = Template(asound_data)
        return asound_template.safe_substitute(
            input=alsa_input, output=alsa_output
        )
