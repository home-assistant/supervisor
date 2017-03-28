#!/bin/bash

set -e

BUILD_CONTAINER_NAME=yocto-build-$$
DOCKER_REPO=pvizeli

cleanup() {
    echo "[INFO] Cleanup."

    # Stop docker container
    echo "[INFO] Cleaning up yocto-build container."
    docker stop $BUILD_CONTAINER_NAME 2> /dev/null || true
    docker rm --volumes $BUILD_CONTAINER_NAME 2> /dev/null || true

    if [ "$1" == "fail" ]; then
        exit 1
    fi
}
trap 'cleanup fail' SIGINT SIGTERM

# Sanity checks
if [ "$#" -ne 2 ]; then
    echo "Usage: create_resinos.sh <MACHINE> <HASSIO_VERSION>"
    echo "Optional environment: BUILD_DIR, PERSISTENT_WORKDIR, RESIN_BRANCH, HASSIO_ROOT"
    exit 1
fi

# Get the absolute script location
pushd `dirname $0` > /dev/null 2>&1
SCRIPTPATH=`pwd`
popd > /dev/null 2>&1

MACHINE=$1
SUPERVISOR_TAG=$2
HASSIO_VERSION=$2
PERSISTENT_WORKDIR=${PERSISTENT_WORKDIR:=~/yocto}
BUILD_DIR=${BUILD_DIR:=$SCRIPTPATH}
WORKSPACE=${BUILD_DIR:=$SCRIPTPATH}/resin-board
HASSIO_ROOT=${HASSIO_ROOT:=$SCRIPTPATH/../..}
DOWNLOAD_DIR=$PERSISTENT_WORKDIR/shared-downloads
SSTATE_DIR=$PERSISTENT_WORKDIR/$MACHINE/sstate
RESIN_BRANCH=${RESIN_BRANCH:=2.0.0-rc5}

# evaluate git repo and arch
case $MACHINE in
    "raspberrypi" | "raspberrypi2" | "raspberrypi3")
        ARCH="armhf"
        RESIN_REPO="https://github.com/resin-os/resin-raspberrypi"
        HOMEASSISTANT_REPOSITORY="$DOCKER_REPO/$MACHINE-homeassistant"
    ;;
    *)
        echo "[ERROR] ${MACHINE} unknown!"
        exit 1
    ;;
esac

echo "[INFO] Checkout repository"
if [ ! -d $WORKSPACE ]; then
    mkdir -p $BUILD_DIR
    cd $BUILD_DIR && git clone $RESIN_REPO resin-board
    if [ $RESIN_BRANCH != "master" ]; then
        cd $WORKSPACE && git checkout $RESIN_BRANCH
    fi
    cd $WORKSPACE && git submodule update --init --recursive
fi

echo "[INFO] Inject HassIO yocto layer"
cp -fr $HASSIO_ROOT/meta-hassio $WORKSPACE/layers/
if [ ! -d $WORKSPACE/build/conf ]; then
    sed -i 's%${TOPDIR}/../layers/meta-resin/meta-resin-common \\%${TOPDIR}/../layers/meta-resin/meta-resin-common \\\n${TOPDIR}/../layers/meta-hassio \\%g' $WORKSPACE/layers/*/conf/samples/bblayers.conf.sample
fi

# Additional variables
BARYS_ARGUMENTS_VAR="-a HASSIO_SUPERVISOR_TAG=$SUPERVISOR_TAG -a HOMEASSISTANT_REPOSITORY=$HOMEASSISTANT_REPOSITORY"

# Make sure shared directories are in place
mkdir -p $DOWNLOAD_DIR
mkdir -p $SSTATE_DIR

# Run build
echo "[INFO] Init docker build."
docker stop $BUILD_CONTAINER_NAME 2> /dev/null || true
docker rm --volumes $BUILD_CONTAINER_NAME 2> /dev/null || true
docker run --rm \
    -v $WORKSPACE:/yocto/resin-board \
    -v $DOWNLOAD_DIR:/yocto/shared-downloads \
    -v $SSTATE_DIR:/yocto/shared-sstate \
    -e BUILDER_UID=$(id -u) \
    -e BUILDER_GID=$(id -g) \
    --name $BUILD_CONTAINER_NAME \
    --privileged \
    pvizeli/yocto-build-env \
    /run-resinos.sh \
        --log \
        --machine "$MACHINE" \
        ${BARYS_ARGUMENTS_VAR} \
        --shared-downloads /yocto/shared-downloads \
        --shared-sstate /yocto/shared-sstate \
        --resinio

# Write deploy artifacts
BUILD_DEPLOY_DIR=$WORKSPACE/deploy
DEVICE_TYPE_JSON=$WORKSPACE/$MACHINE.json
VERSION_HOSTOS=$(cat $WORKSPACE/build/tmp/deploy/images/$MACHINE/VERSION_HOSTOS)

DEPLOY_ARTIFACT=$(jq --raw-output '.yocto.deployArtifact' $DEVICE_TYPE_JSON)
COMPRESSED=$(jq --raw-output '.yocto.compressed' $DEVICE_TYPE_JSON)
ARCHIVE=$(jq --raw-output '.yocto.archive' $DEVICE_TYPE_JSON)
mkdir -p $BUILD_DEPLOY_DIR
rm -rf $BUILD_DEPLOY_DIR/* # do we have anything there?
cp $(readlink --canonicalize $WORKSPACE/build/tmp/deploy/images/$MACHINE/$DEPLOY_ARTIFACT) $BUILD_DEPLOY_DIR/$DEPLOY_ARTIFACT
if [ "${COMPRESSED}" == 'true' ]; then
	if [ "${ARCHIVE}" == 'true' ]; then
		(cd $BUILD_DEPLOY_DIR && tar --remove-files  --use-compress-program pigz --directory=$DEPLOY_ARTIFACT -cvf ${DEPLOY_ARTIFACT}.tar.gz .)
	else
		 mv $BUILD_DEPLOY_DIR/$DEPLOY_ARTIFACT $BUILD_DEPLOY_DIR/resin.img
		(cd $BUILD_DEPLOY_DIR && tar --remove-files --use-compress-program pigz -cvf resin.img.tar.gz resin.img)
	fi
fi
if [ -f $(readlink --canonicalize $WORKSPACE/build/tmp/deploy/images/$MACHINE/resin-image-$MACHINE.resinhup-tar) ]; then
    mv -v $(readlink --canonicalize $WORKSPACE/build/tmp/deploy/images/$MACHINE/resin-image-$MACHINE.resinhup-tar) $BUILD_DEPLOY_DIR/resinhup-$VERSION_HOSTOS.tar
else
    echo "WARNING: No resinhup package found."
fi

cp $WORKSPACE/build/tmp/deploy/images/$MACHINE/VERSION $BUILD_DEPLOY_DIR || true
cp $WORKSPACE/build/tmp/deploy/images/$MACHINE/VERSION_HOSTOS $BUILD_DEPLOY_DIR || true
cp $DEVICE_TYPE_JSON $BUILD_DEPLOY_DIR/device-type.json
# move to deploy directory the kernel modules headers so we have it as a build artifact in jenkins
cp $WORKSPACE/build/tmp/deploy/images/$MACHINE/kernel_modules_headers.tar.gz $BUILD_DEPLOY_DIR || true

echo "INFO: Pushing resinhup package to dockerhub"
DOCKER_IMAGE="$DOCKER_REPO/hassio"
DOCKER_TAG="$HASSIO_VERSION-$MACHINE"
if [ -f $BUILD_DEPLOY_DIR/resinhup-$VERSION_HOSTOS.tar ]; then
    docker import $BUILD_DEPLOY_DIR/resinhup-$VERSION_HOSTOS.tar $DOCKER_IMAGE:$DOCKER_TAG
    docker push $DOCKER_IMAGE:$DOCKER_TAG
    docker rmi $DOCKER_IMAGE:$DOCKER_TAG # cleanup
else
    echo "ERROR: The build didn't produce a resinhup package."
    exit 1
fi

# Cleanup the build directory
# Keep this after writing all artifacts
exit 0
rm -rf $WORKSPACE/build
