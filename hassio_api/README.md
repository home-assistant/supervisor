# HassIO Server

## REST API Supervisor

### /supervisor_info

### /supervisor_network
- Payload: {'hostname': '', 'mode': 'dhcp|fixed', 'ssid': '', 'ip': '', 'netmask': '', 'gateway': ''}

### /supervisor_power
- Payload: {'action': 'reboot|shutdown'}

## REST API HomeAssistant

### /homeassistant_info

### /homeassistant_update
- Payload: {'version': '0.XX.Y'}
If version is None it read last version from server.

## REST API addons

### /addons_info

### /addons_run
- Payload: {'addon': 'xy', 'options': {}}

### /addons_stop
- Payload: {'addon': 'xy'}

### /addons_install
- Payload: {'addon': 'xy'}

### /addons_delete
- Payload: {'addon': 'xy'}

### /addons_update
- Payload: {'addon': 'xy', 'version': 'x.x'}
If version is None it read last version from server.
