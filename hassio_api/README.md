# HassIO Server

## REST API Supervisor

### /supervisor/info

### /supervisor/network
- Payload: {'hostname': '', 'mode': 'dhcp|fixed', 'ssid': '', 'ip': '', 'netmask': '', 'gateway': ''}

### /supervisor/reboot

### /supervisor/shutdown

## REST API HomeAssistant

### /homeassistant/info

### /homeassistant/update
- Payload: {'version': '0.XX.Y'}
If version is None it read last version from server.

## REST API addons

### /addons/info

### /addons/reload

### /addons/{addon}/start
- Payload: {'options': {}}

### /addons/{addon}/stop

### /addons/{addon}/install
- Payload: {'version': 'x.x'}

### /addons/{addon}/uninstall

### /addons/{addon}/update
- Payload: {'version': 'x.x'}

If version is None it read last version from server.
