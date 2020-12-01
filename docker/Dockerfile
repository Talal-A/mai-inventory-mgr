FROM ubuntu:16.04

MAINTAINER talal "talal.abouhaiba@gmail.com"

RUN apt-get update && apt-get install -y \
        software-properties-common
    RUN add-apt-repository ppa:deadsnakes/ppa
    RUN apt-get update && apt-get install -y \
        python3.7 \
        python3-pip \
        wget
    RUN python3.7 -m pip install pip

RUN apt remove python-flask

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN python3.7 --version
RUN python3.7 -m pip install -r requirements.txt
RUN python3.7 -m pip list

COPY . /app

ENTRYPOINT [ "python3.7" ]

CMD [ "run.py" ]
