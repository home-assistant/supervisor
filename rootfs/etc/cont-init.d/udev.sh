#!/usr/bin/with-contenv bashio
# ==============================================================================
# Start udev service
# ==============================================================================
udevd --daemon

bashio::log.info "Update udev information"
if udevadm trigger; then
    udevadm settle || true
else
    bashio::log.warning "Triggering of udev rules fails!"
fi
