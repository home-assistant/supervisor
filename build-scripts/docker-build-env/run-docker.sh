#!/bin/bash

set -e

DOCKER_TIMEOUT=20 # Wait 20 seconds for docker to start

cleanup() {
    echo "[INFO] Running cleanup..."

    # Stop docker gracefully
    echo "[INFO] Stopping in container docker..."
    DOCKERPIDFILE=/var/run/docker.pid
    if [ -f $DOCKERPIDFILE ] && [ -s $DOCKERPIDFILE ] && ps $(cat $DOCKERPIDFILE) | grep -q docker; then
        kill $(cat $DOCKERPIDFILE)
        # Now wait for it to die
        STARTTIME=$(date +%s)
        ENDTIME=$(date +%s)
        while [ -f $DOCKERPIDFILE ] && [ -s $DOCKERPIDFILE ] && ps $(cat $DOCKERPIDFILE) | grep -q docker; do
            if [ $(($ENDTIME - $STARTTIME)) -le $DOCKER_TIMEOUT ]; then
                sleep 1
                ENDTIME=$(date +%s)
            else
                echo "[ERROR] Timeout while waiting for in container docker to die."
                exit 1
            fi
        done
    else
        echo "[WARN] Can't stop docker container."
        echo "[WARN] Your host might have been left with unreleased resources (ex. loop devices)."
    fi

    if [ "$1" == "fail" ]; then
        exit 1
    fi
}
trap 'cleanup fail' SIGINT SIGTERM

# Start docker
echo "[INFO] Starting docker."
dockerd 2> /dev/null &
echo "[INFO] Waiting for docker to initialize..."
STARTTIME=$(date +%s)
ENDTIME=$(date +%s)
until docker info >/dev/null 2>&1; do
    if [ $(($ENDTIME - $STARTTIME)) -le $DOCKER_TIMEOUT ]; then
        sleep 1
        ENDTIME=$(date +%s)
    else
        echo "[ERROR] Timeout while waiting for docker to come up."
        exit 1
    fi
done
echo "[INFO] Docker was initialized."

# Start barys with all the arguments requested
echo "[INFO] Running build..."

cleanup
exit 0
