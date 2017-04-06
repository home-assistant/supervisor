# HassIO Server

## Host Controll

Communicate over unix socket with a host daemon.

- commands
```
# info
-> {'os', 'version', 'level', 'hostname'}
# reboot
# shutdown
# host-update [v]
# supervisor-update [v]

# network info
# network hostname xy
# network wlan ssd xy
# network wlan password xy
# network int ip xy
# network int netmask xy
# network int route xy
```

level:
- 1: power functions
- 2: supervisor update
- 4: host update
- 8: network functions

Answer:
```
{}|OK|ERROR|WRONG
```

- {}: json
- OK: call was successfully
- ERROR: error on call
- WRONG: not supported

## HassIO REST API

Interface for HomeAssistant to controll things from supervisor.

On error:
```json
{
    "result": "error",
    "message": ""
}
```

On success
```json
{
    "result": "ok",
    "data": { }
}
```

### HassIO

- `/supervisor/info`

```json
{
    "version": INSTALL_VERSION,
    "current": CURRENT_VERSION
}
```

- `/supervisor/update`
Payload: {"version": "0.XX"}
If version is None it read last version from server.

- `/supervisor/option`
Payload: {"beta": true|false}

### Host

- `/host/shutdown`

- `/host/reboot`

- `/host/info`

See HostControll info command.

- `/host/update`
On some device we support host upates. Like ResinOS.

### Network

- `/network/info`

- `/network/options`
Payload: {'hostname': '', 'mode': 'dhcp|fixed', 'ssid': '', 'ip': '', 'netmask': '', 'gateway': ''}


### HomeAssistant

- `/homeassistant/info`

```json
{
    "version": INSTALL_VERSION,
    "current": CURRENT_VERSION
}
```

- `/homeassistant/update`
Payload: {"version": "0.XX.Y"}
If version is None it read last version from server.

### REST API addons

- `/addons/info`

- `/addons/{addon}/options`
Payload: {'options': {}}

- `/addons/{addon}/start`

- `/addons/{addon}/stop`

- `/addons/{addon}/install`
Payload: {"version": "x.x"}

- `/addons/{addon}/uninstall`

- `/addons/{addon}/update`
Payload: {"version": "x.x"}
If version is None it read last version from server.
