
# HassIO supervisor

- Docker socket for Docker management
- HassIO HostControll socket for manage host functions
- Persistent volume to store all data

## Run supervisor on a normal docker host

```bash
docker run --privileged --name resin_supervisor \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /var/run/hassio_hc.sock:/var/run/hassio-hc.sock \
    -v /resin-data:/data \
    -v /var/log/supervisor-log:/var/log \
    -e DOCKER_SOCKET=/var/run/docker.sock \
    -e HASSIO_HC_SOCKET=/var/run/hassio-hc.sock \
    -e SUPERVISOR_SHARE=/resin-data \
    -e SUPERVISOR_NAME=resin_supervisor \
    -e HOMEASSISTANT_REPOSITORY=${HOMEASSISTANT_REPOSITORY} \
    ${SUPERVISOR_IMAGE}
```
