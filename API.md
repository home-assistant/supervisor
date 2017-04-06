# HassIO Server

## Host Controll

Communicate over unix socket with a host daemon.

- commands
```
# info
-> {'os', 'version', 'current', 'level', 'hostname'}
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
    "version": "INSTALL_VERSION",
    "current": "CURRENT_VERSION",
    "beta": "true|false",
    "addons": {}
}
```

- `/supervisor/update`
Optional:
```json
{
    "version": "VERSION"
}
```

- `/supervisor/option`
```json
{
    "beta": "true|false"
}
```

### Host

- `/host/shutdown`

- `/host/reboot`

- `/host/info`
See HostControll info command.
```json
{
    "os": "",
    "version": "",
    "current": "",
    "level": "",
    "hostname": "",
}
```

- `/host/update`
Optional:
```json
{
    "version": "VERSION"
}
```

### Network

- `/network/info`

- `/network/options`
```json
{
    "hostname": "",
    "mode": "dhcp|fixed",
    "ssid": "",
    "ip": "",
    "netmask": "",
    "gateway": ""
}
```

### HomeAssistant

- `/homeassistant/info`

```json
{
    "version": "INSTALL_VERSION",
    "current": "CURRENT_VERSION"
}
```

- `/homeassistant/update`
Optional:
```json
{
    "version": "VERSION"
}
```

### REST API addons

- `/addons/{addon}/info`
```json
{
    "version": "VERSION",
    "current": "CURRENT_VERSION",
    "state": "started|stopped",
    "boot": "auto|manual",
    "options": {},
}
```

- `/addons/{addon}/options`
```json
{ }
```

- `/addons/{addon}/start`

- `/addons/{addon}/stop`

- `/addons/{addon}/install`
Optional:
```json
{
    "version": "VERSION"
}
```

- `/addons/{addon}/uninstall`

- `/addons/{addon}/update`
Optional:
```json
{
    "version": "VERSION"
}
```
