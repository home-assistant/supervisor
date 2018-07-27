ARG BUILD_FROM
FROM $BUILD_FROM

# Add env
ENV LANG C.UTF-8

# Setup base
COPY requirements.txt /usr/src/
RUN apk add --no-cache \
        git \
        socat \
        glib \
        libstdc++ \
        eudev-libs \
    && apk add --no-cache --virtual .build-dependencies \
        make \
        g++ \
    && pip3 install -r /usr/src/requirements.txt \
    && apk del .build-dependencies \
    && rm -f /usr/src/requirements.txt

# Install HassIO
COPY . /usr/src/hassio
RUN pip3 install --no-cache-dir /usr/src/hassio \
    && rm -rf /usr/src/hassio

CMD [ "python3", "-m", "hassio" ]
