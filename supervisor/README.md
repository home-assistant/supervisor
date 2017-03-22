
## Run supervisor on a normal docker host

```bash
docker run --privileged --name resin_supervisor \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $CONFIG_PATH:/boot/config.json  \
    -v $BOOT_MOUNTPOINT/system-connections/resin-sample:/boot/network \
    -v /resin-data/resin-supervisor:/data \
    -v /resin-data:/shared-data \
    -v /var/log/supervisor-log:/var/log \
    -e DOCKER_ROOT=/mnt/root/var/lib/docker \
    -e DOCKER_SOCKET=/var/run/docker.sock \
    -e SUPERVISOR_IMAGE=${SUPERVISOR_IMAGE} \
    -e SUPERVISOR_TAG=${SUPERVISOR_TAG} \
    -e SUPERVISOR_SHARE=/resin-data \
    -e SUPERVISOR_NAME=resin_supervisor \
    -e HOMEASSISTANT_REPOSITORY=${HOMEASSISTANT_REPOSITORY} \
    ${SUPERVISOR_IMAGE}
```
