[![Build Status](https://dev.azure.com/home-assistant/supervisor/_apis/build/status/Release?branchName=dev)](https://dev.azure.com/home-assistant/supervisor/_build/latest?definitionId=60&branchName=dev)

# Home Assistant Supervisor

## First private cloud solution for home automation

Hass.io is a Docker-based system for managing your Home Assistant installation
and related applications. The system is controlled via Home Assistant which
communicates with the Supervisor. The Supervisor provides an API to manage the
installation. This includes changing network settings or installing
and updating software.

## Installation

Installation instructions can be found at <https://home-assistant.io/hassio>.

## Development

The development of the supervisor is a bit tricky. Not difficult but tricky.

- You can use the builder to build your supervisor: https://github.com/home-assistant/hassio-builder
- Go into a HassOS device or VM and pull your supervisor.
- Set the developer modus with cli `hassio supervisor options --channel=dev`
- Tag it as `homeassistant/xy-hassio-supervisor:latest`
- Restart the service like `systemctl restart hassos-supervisor | journalctl -fu hassos-supervisor`
- Test your changes

Small Bugfix or improvements, make a PR. Significant change makes first an RFC.
