# Hass.io

## First private cloud solution for home automation

Hass.io is a Docker-based system for managing your Home Assistant installation
and related applications. The system is controlled via Home Assistant which
communicates with the Supervisor. The Supervisor provides an API to manage the
installation. This includes changing network settings or installing
and updating software.

![](misc/hassio.png?raw=true)

## Installation

Installation instructions can be found at <https://home-assistant.io/hassio>.

## Development

The development of the supervisor is a bit tricky. Not difficult but tricky.

- You can use the builder to build your supervisor: https://github.com/home-assistant/hassio-build/tree/master/builder
- Go into a HassOS device or VM and pull your supervisor.
- Set the developer modus on updater.json
- Tag it as homeassistant/xy-hassio-supervisor:latest
- Restart the service like systemctl restart hassos-supervisor | journalctl -fu hassos-supervisor
- Test your changes

Small Bugfix or improvements, make a PR. Significant change makes first an RFC.
