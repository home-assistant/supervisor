ARG BUILD_FROM
FROM ${BUILD_FROM}

ENV \
    S6_SERVICES_GRACETIME=10000 \
    SUPERVISOR_API=http://localhost \
    CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1 \
    UV_SYSTEM_PYTHON=true

ARG \
    COSIGN_VERSION

# Install base
WORKDIR /usr/src
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
    && curl -Lso /usr/bin/cosign "https://github.com/home-assistant/cosign/releases/download/${COSIGN_VERSION}/cosign_${BUILD_ARCH}" \
    && chmod a+x /usr/bin/cosign \
    && pip3 install uv==0.9.18

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
COPY . supervisor
RUN \
    uv pip install --no-cache -e ./supervisor \
    && python3 -m compileall ./supervisor/supervisor


WORKDIR /
COPY rootfs /
