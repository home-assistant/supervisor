#!/bin/bash

set -o errexit

groupadd -g $BUILDER_GID builder
useradd -m -u $BUILDER_UID -g $BUILDER_GID builder

sudo -H -u builder /bin/bash -c "cd /yocto/image \
	&& source oe-core/oe-init-build-env build bitbake \
	&& DL_DIR=/yocto/shared-downloads SSTATE_DIR=/yocto/shared-sstate MACHINE=$TARGET_MACHINE /yocto/image/bitbake/bin/bitbake core-image-minimal"

cp --dereference /yocto/image/build/tmp-glibc/deploy/images/$TARGET_MACHINE/core-image-minimal-$TARGET_MACHINE.tar.gz  /yocto/image/rootfs.tar.gz
