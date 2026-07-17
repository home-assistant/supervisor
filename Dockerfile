ARG BUILD_FROM=ghcr.io/home-assistant/base-python:3.14-alpine3.24-2026.06.1
FROM ${BUILD_FROM} AS supervisor-base

ENV \
    S6_SERVICES_GRACETIME=415000 \
    S6_KILL_GRACETIME=3000 \
    SUPERVISOR_API=http://localhost \
    CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1 \
    UV_SYSTEM_PYTHON=true

# Install OS packages used both by build and final image
RUN \
    set -x \
    && apk add --no-cache \
        findutils \
        eudev \
        eudev-libs \
        git \
        libffi \
        libpulse \
        musl \
        openssl \
        yaml \
    \
    && pip3 install uv==0.10.9

#############################################
# Install requirements and build Supervisor #
#############################################

FROM supervisor-base AS supervisor-build

WORKDIR /usr/src

# Install requirements
RUN \
    --mount=type=bind,source=./requirements.txt,target=/usr/src/requirements.txt \
    --mount=type=bind,source=./wheels,target=/usr/src/wheels \
    if ls /usr/src/wheels/musllinux/* >/dev/null 2>&1; then \
        LOCAL_WHEELS=/usr/src/wheels/musllinux; \
        echo "Using local wheels from: $LOCAL_WHEELS"; \
    else \
        LOCAL_WHEELS=; \
        echo "No local wheels found"; \
    fi && \
    uv pip install --compile-bytecode --no-cache --no-build \
        -r requirements.txt \
        ${LOCAL_WHEELS:+--find-links $LOCAL_WHEELS}

# Install Home Assistant Supervisor
ARG BUILD_VERSION="9999.09.9.dev9999"
COPY . supervisor
RUN \
    --mount=type=bind,source=./wheels,target=/usr/src/wheels \
    if ls /usr/src/wheels/musllinux/* >/dev/null 2>&1; then \
        LOCAL_WHEELS=/usr/src/wheels/musllinux; \
        echo "Using local wheels from: $LOCAL_WHEELS"; \
    else \
        LOCAL_WHEELS=; \
        echo "No local wheels found"; \
    fi \
    && sed -i "s/^SUPERVISOR_VERSION =.*/SUPERVISOR_VERSION = \"${BUILD_VERSION}\"/g" /usr/src/supervisor/supervisor/const.py \
    && uv pip install --no-cache -e ./supervisor \
        ${LOCAL_WHEELS:+--find-links $LOCAL_WHEELS} \
    && python3 -m compileall ./supervisor/supervisor

# Copy the rest of rootfs files
COPY rootfs /

#########################
# Final flattened image #
#########################

FROM supervisor-base

# Copy everything from the build stage as a single layer
COPY --from=supervisor-build / /

LABEL \
    io.hass.type="supervisor" \
    org.opencontainers.image.title="Home Assistant Supervisor" \
    org.opencontainers.image.description="Container-based system for managing Home Assistant Core installation" \
    org.opencontainers.image.authors="The Home Assistant Authors" \
    org.opencontainers.image.url="https://www.home-assistant.io/" \
    org.opencontainers.image.documentation="https://www.home-assistant.io/docs/" \
    org.opencontainers.image.licenses="Apache License 2.0"
