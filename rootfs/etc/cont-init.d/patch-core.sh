#!/usr/bin/with-contenv bashio
# ==============================================================================
# Patching Home Assistant Core
# ==============================================================================

# Start with 0.111 there is a global constant for handling max core startup time
# we can handle that better and avoid migration issue on database.
sed -i "s|TIMEOUT_EVENT_BOOTSTRAP = .+|TIMEOUT_EVENT_BOOTSTRAP = 0|" /usr/src/homeassistant/homeassistant/bootstrap.py || true
