ARG BUILD_FROM
FROM $BUILD_FROM

# Add env
ENV LANG C.UTF-8

# Setup base
RUN apk add --no-cache \
        python3 \
        git \
        socat \
        glib \
        libstdc++ \
        eudev-libs \
    && apk add --no-cache --virtual .build-dependencies \
        make \
        python3-dev \
        g++ \
    && pip3 install --no-cache-dir \
        uvloop==0.10.2 \
        cchardet==2.1.1 \
        pycryptodome==3.4.11 \
    && apk del .build-dependencies

# Install HassIO
COPY . /usr/src/hassio
RUN pip3 install --no-cache-dir /usr/src/hassio \
    && rm -rf /usr/src/hassio

CMD [ "python3", "-m", "hassio" ]
