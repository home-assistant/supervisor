#!/bin/bash

set -e

BUILD_CONTAINER_NAME=resinhup-build-$$
DOCKER_REPO=pvizeli

cleanup() {
    echo "[INFO] Cleanup."

    # Stop docker container
    echo "[INFO] Cleaning up homeassistant-build container."
    docker stop $BUILD_CONTAINER_NAME 2> /dev/null || true
    docker rm --volumes $BUILD_CONTAINER_NAME 2> /dev/null || true

    if [ "$1" == "fail" ]; then
        exit 1
    fi
}
trap 'cleanup fail' SIGINT SIGTERM

# Sanity checks
if [ "$#" -ne 2 ]; then
    echo "Usage: create_resinhup.sh <VERS> <MACHINE>"
    echo "Optional environment: BUILD_DIR"
    exit 1
fi

# Get the absolute script location
pushd `dirname $0` > /dev/null 2>&1
SCRIPTPATH=`pwd`
popd > /dev/null 2>&1

MACHINE=$2
RESINHUP_VER=$1
BASE_IMAGE="resin\/${MACHINE}-python:3.6"
DOCKER_TAG=${MACHINE}-${RESINHUP_VER}
DOCKER_IMAGE=resinhup
BUILD_DIR=${BUILD_DIR:=$SCRIPTPATH}
WORKSPACE=${BUILD_DIR:=$SCRIPTPATH}/resinhup

# evaluate git repo and arch
case $MACHINE in
    "raspberrypi3")
        DOCKER_FILE_NAME="Dockerfile.raspberrypi3"
    ;;
    "raspberrypi2")
        DOCKER_FILE_NAME="Dockerfile.raspberryp-i2"
    ;;
    "raspberrypi")
        DOCKER_FILE_NAME="Dockerfile.raspberry-pi"
    ;;
    *)
        echo "[ERROR] ${MACHINE} unknown!"
        exit 1
    ;;
esac

# setup docker
echo "[INFO] Setup workspace"
mkdir -p $BUILD_DIR

git clone https://github.com/resin-os/resinhup $WORKSPACE
cd $WORKSPACE && git checkout $DOCKER_TAG

cp $DOCKER_FILE_NAME Dockerfile

# Run build
echo "[INFO] start docker build"
docker stop $BUILD_CONTAINER_NAME 2> /dev/null || true
docker rm --volumes $BUILD_CONTAINER_NAME 2> /dev/null || true
docker run --rm \
    -v $WORKSPACE:/docker \
    -v ~/.docker:/root/.docker \
    -e DOCKER_REPO=$DOCKER_REPO \
    -e DOCKER_IMAGE=$DOCKER_IMAGE \
    -e DOCKER_TAG=$DOCKER_TAG \
    --name $BUILD_CONTAINER_NAME \
    --privileged \
    pvizeli/docker-build-env \
    /run-docker.sh

echo "[INFO] cleanup WORKSPACE"
cd $BUILD_DIR
rm -rf $WORKSPACE

cleanup
exit 0
