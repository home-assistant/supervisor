# HassIO
### First private cloud solution for home automation.

Hass.io is a Docker based system for managing your Home Assistant installation and related applications. The system is controlled via Home Assistant which communicates with the supervisor. The supervisor provides an API to manage the installation. This includes changing network settings or installing and updating software.

![](misc/hassio.png?raw=true)

[HassIO-Addons](https://github.com/home-assistant/hassio-addons) | [HassIO-Build](https://github.com/home-assistant/hassio-build)

**HassIO is under active development and is not ready yet for production use.**

## Installing Hass.io

- Generic Linux installation: https://github.com/home-assistant/hassio-build/tree/master/install
- Hardware Images: https://github.com/home-assistant/hassio-build/blob/master/meta-hassio/

## Feature in progress
- Backup/Restore
- DHCP-Server addon

# HomeAssistant

## SSL

All addons that create SSL certs follow the same file structure. If you use one, put follow lines in your `configuration.yaml`.

```yaml
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
```
