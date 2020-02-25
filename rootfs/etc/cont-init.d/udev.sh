#!/usr/bin/with-contenv bashio
# ==============================================================================
# Start udev service
# ==============================================================================
udevd --daemon

bashio::log.info "Update udev informations"
udevadm trigger
udevadm settle