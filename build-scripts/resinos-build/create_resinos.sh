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
    echo "Usage: create_resinos.sh <MACHINE> <SUPERVISOR_TAG>"
    echo "Optional environment: BUILD_DIR, PERSISTENT_WORKDIR, RESIN_BRANCH"
    exit 1
fi

# Get the absolute script location
pushd `dirname $0` > /dev/null 2>&1
SCRIPTPATH=`pwd`
popd > /dev/null 2>&1

MACHINE=$1
PERSISTENT_WORKDIR=${PERSISTENT_WORKDIR:=~/yocto}
BUILD_DIR=${BUILD_DIR:=$SCRIPTPATH}
WORKSPACE=${BUILD_DIR:=$SCRIPTPATH}/resin-board
DOWNLOAD_DIR=$PERSISTENT_WORKDIR/shared-downloads
SSTATE_DIR=$PERSISTENT_WORKDIR/$MACHINE/sstate
RESIN_BRANCH=${RESIN_BRANCH:=master}

# evaluate git repo and arch
case $MACHINE in
    "raspberrypi3" | "raspberrypi2" | "raspberrypi")
        ARCH="armhf"
        RESIN_REPO="https://github.com/resin-os/resin-raspberrypi"
    ;;
    *)
        echo "[ERROR] ${MACHINE} unknown!"
        exit 1
    ;;
esac

echo "[INFO] Checkout repository"
mkdir -p $BUILD_DIR
cd $BUILD_DIR && git clone $RESIN_REPO resin-board
if [ $RESIN_BRANCH != "master" ]; then
    cd $WORKSPACE && git checkout $RESIN_BRANCH
fi
cd $WORKSPACE && git submodule update --init --recursive

echo "[INFO] Inject HassIO yocto layer"
cp -r ../../meta-hassio $WORKSPACE/layer/

# Additional variables
BARYS_ARGUMENTS_VAR="-a HASSIO_SUPERVISOR_TAG=$SUPERVISOR_TAG"

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
        --remove-build \
        --machine "$MACHINE" \
        ${BARYS_ARGUMENTS_VAR} \
        --shared-downloads /yocto/shared-downloads \
        --shared-sstate /yocto/shared-sstate \
        --rm-work

exit
# Write deploy artifacts
BUILD_DEPLOY_DIR=$WORKSPACE/deploy
DEVICE_TYPE_JSON=$WORKSPACE/$MACHINE.json
VERSION_HOSTOS=$(cat $WORKSPACE/build/tmp/deploy/images/$MACHINE/VERSION_HOSTOS)

DEPLOY_ARTIFACT=$(jq --raw-output '.yocto.deployArtifact' $DEVICE_TYPE_JSON)
COMPRESSED=$(jq --raw-output '.yocto.compressed' $DEVICE_TYPE_JSON)
ARCHIVE=$(jq --raw-output '.yocto.archive' $DEVICE_TYPE_JSON)
mkdir -p $BUILD_DEPLOY_DIR
rm -rf $BUILD_DEPLOY_DIR/* # do we have anything there?
mv -v $(readlink --canonicalize $WORKSPACE/build/tmp/deploy/images/$MACHINE/$DEPLOY_ARTIFACT) $BUILD_DEPLOY_DIR/$DEPLOY_ARTIFACT
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

mv -v $WORKSPACE/build/tmp/deploy/images/$MACHINE/VERSION $BUILD_DEPLOY_DIR
mv -v $WORKSPACE/build/tmp/deploy/images/$MACHINE/VERSION_HOSTOS $BUILD_DEPLOY_DIR
cp $DEVICE_TYPE_JSON $BUILD_DEPLOY_DIR/device-type.json
# move to deploy directory the kernel modules headers so we have it as a build artifact in jenkins
mv -v $WORKSPACE/build/tmp/deploy/images/$MACHINE/kernel_modules_headers.tar.gz $BUILD_DEPLOY_DIR

# If this is a clean production build, push a resinhup package to dockerhub
# and registry.resinstaging.io.
if [[ "$sourceBranch" == production* ]] && [ "$metaResinBranch" == "__ignore__" ] && [ "$supervisorTag" == "__ignore__" ]; then
    echo "INFO: Pushing resinhup package to dockerhub and registry.resinstaging.io."
    SLUG=$(jq --raw-output '.slug' $DEVICE_TYPE_JSON)
    DOCKER_REPO="resin/resinos"
    DOCKER_TAG="$VERSION_HOSTOS-$SLUG"
    RESINREG_REPO="registry.resinstaging.io/resin/resinos"
    RESINREG_TAG="$VERSION_HOSTOS-$SLUG"
    if [ -f $BUILD_DEPLOY_DIR/resinhup-$VERSION_HOSTOS.tar ]; then
        docker import $BUILD_DEPLOY_DIR/resinhup-$VERSION_HOSTOS.tar $DOCKER_REPO:$DOCKER_TAG
        docker push $DOCKER_REPO:$DOCKER_TAG
        docker rmi $DOCKER_REPO:$DOCKER_TAG # cleanup

        docker import $BUILD_DEPLOY_DIR/resinhup-$VERSION_HOSTOS.tar $RESINREG_REPO:$RESINREG_TAG
        docker push $RESINREG_REPO:$RESINREG_TAG
        docker rmi $RESINREG_REPO:$RESINREG_TAG # cleanup
    else
        echo "ERROR: The build didn't produce a resinhup package."
        exit 1
    fi
else
    echo "WARNING: There is no need to upload resinhup package for a non production clean build."
fi

# Cleanup the build directory
# Keep this after writing all artifacts
rm -rf $WORKSPACE/build
