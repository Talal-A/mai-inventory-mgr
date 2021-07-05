FROM ubuntu:16.04

MAINTAINER talal "talal.abouhaiba@gmail.com"

RUN apt-get update && apt-get install -y \
        software-properties-common
    RUN add-apt-repository ppa:deadsnakes/ppa
    RUN apt-get update && apt-get install -y \
        python3.7 \
        python3-pip \
        wget \
        tzdata
    RUN python3.7 -m pip install pip

RUN apt remove python-flask

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN python3.7 --version
RUN python3.7 -m pip install -r requirements.txt
RUN python3.7 -m pip list

COPY . /app

# Download litestream
ADD https://github.com/benbjohnson/litestream/releases/download/v0.3.4/litestream-v0.3.4-linux-amd64-static.tar.gz /tmp/litestream.tar.gz
RUN tar -C /usr/local/bin -xzf /tmp/litestream.tar.gz

# Install s6-overlay
ADD https://github.com/just-containers/s6-overlay/releases/download/v2.2.0.3/s6-overlay-amd64-installer /tmp/
RUN chmod +x /tmp/s6-overlay-amd64-installer
RUN /tmp/s6-overlay-amd64-installer /

# Copy s6 init & service definitions.
COPY etc/cont-init.d /etc/cont-init.d
COPY etc/services.d /etc/services.d

# Copy Litestream configuration file.
COPY etc/litestream.yml /etc/litestream.yml

# The kill grace time is set to zero because our app handles shutdown through SIGTERM.
ENV S6_KILL_GRACETIME=0

# Sync disks is enabled so that data is properly flushed.
ENV S6_SYNC_DISKS=1

EXPOSE 9205

# Run the s6 init process on entry.
ENTRYPOINT [ "/init" ]