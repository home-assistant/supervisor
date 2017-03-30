# HassIO
First private cloud solution for home automation.

It is a docker image (supervisor) they manage HomeAssistant docker and give a interface to controll itself over UI. It have a own eco system with addons to extend the functionality in a easy way.

## History
- **0.1**: Initial supervisor with setup HomeAssistant docker
- **0.2**: Support for basic HostControll

# Hardware Image
Based on ResinOS and Yocto Linux. It have a preinstall HassIO supervisor and support OTA Updates. That make it maintenanceless. The image have no homeassistant included and they will downloaded after first setup. That need some times and internet brandwith.

https://drive.google.com/drive/folders/0B2o1Uz6l1wVNbFJnb2gwNXJja28?usp=sharing

## History
- **0.2**: Fix some bugs and update it to HassIO 0.2
- **0.1**: First techpreview with dumy supervisor (ResinOS 2.0.0-RC5)

## Network & Hostname
On a boot partition exists `config.json`. Add `"hostname": "xyz"` for change the hostname and access with `hostname.local` to machine. For Network config you can edit `system-connections/resin-sample`.

## Developer access to ResinOS host
You can put your authorized_keys file into boot partition. After a boot it, you can acces to your device over ssh port 22222

## Troubleshooting

Read logoutput from supervisor:
```bash
journalctl -f -u resin-supervisor.service
docker logs homeassistant
```
