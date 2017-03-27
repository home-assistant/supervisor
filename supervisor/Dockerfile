FROM %%BASE_IMAGE%%

# Add version
ENV VERSION %%SUPERVISOR_TAG%%
ENV LANG C.UTF-8

# remove several traces of python
RUN apk del --no-cache python*

# setup base
RUN apk add --no-cache python3 git

# update pip
RUN pip3 install pip --no-cache-dir --upgrade

# install HassIO
COPY hassio_api /usr/src/hassio_api
RUN pip3 install --no-cache-dir /usr/src/hassio_api

CMD [ "python3", "-m", "hassio" ]
