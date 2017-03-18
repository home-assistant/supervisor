# HassIO Server

## REST API

### /supervisor

- GET: Return running version back
- PUT: Read last avilable version and write it to ResinOS config

### /homeassistant

- GET: get avilable version
- PUT: performe homeassistant update

### /addons

- GET: get list of avilable addons and installed addons back
- PUT: get or performe a update of a addon
- POST: install a addon
- DEL: remove a addon
