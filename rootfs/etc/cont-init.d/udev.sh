#!/usr/bin/with-contenv bashio
# ==============================================================================
# Start udev service
# ==============================================================================

if bashio::fs.directory_exists /run/udev; then
    bashio::log.info "Using udev information from host"
    bashio::exit.ok
fi


bashio::log.info "Setup udev backend inside container"
udevd --daemon

if udevadm trigger; then
    udevadm settle || true
else
    bashio::log.warning "Triggering of udev rules fails!"
fi
