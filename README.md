# HassIO
First private cloud solution for home automation.

It is a docker image (supervisor) they manage HomeAssistant docker and give a interface to control itself over UI. It have a own eco system with addons to extend the functionality in a easy way.

![](misc/hassio.png?raw=true)

[HassIO-Addons](https://github.com/home-assistant/hassio-addons) | [HassIO-Build](https://github.com/home-assistant/hassio-build)

**HassIO is at the moment on development and not ready to use productive!**

## Feature in progress
- Backup/Restore
- DHCP-Server addon

# HomeAssistant

## SSL

All addons they can create SSL certs do that in same schema. So you can put follow lines to your `configuration.yaml`.
```yaml
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
```

## Install on a own System

- Generic Linux installation: https://github.com/home-assistant/hassio-build/tree/master/install
- Hardware Images: https://github.com/home-assistant/hassio-build/blob/master/meta-hassio/
