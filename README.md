# HassIO
First private cloud OS for home automation.

It is a docker image (supervisor) they manage HomeAssistant docker and give a interface to controll itself over UI. It have a own eco system with addons to extend the functionality in a easy way.

# Hardware Image
Based on ResinOS and Yocto Linux. It have a preinstall HassIO supervisor and support OTA Updates. That make it maintenanceless.

https://drive.google.com/drive/folders/0B2o1Uz6l1wVNbFJnb2gwNXJja28?usp=sharing

# History

- **0.1**: First techpreview with dumy supervisor
- **0.2**: Support now OTA updates (Need reflush from 0.1)

## Developer access to ResinOS host
You can put your authorized_keys file into boot partition. After a boot it, you can acces to your device over ssh port 22222
