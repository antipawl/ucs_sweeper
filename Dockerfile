FROM artifactory.f5net.com/dockerhub-remote/python:3.8

RUN apt-get -y update && \
    apt-get -y install build-essential libcap-dev rsync pcregrep bind9 vim 

COPY . /sweeper/

WORKDIR /

RUN pip install -r /sweeper/requirements.txt && \
    python --version && \
    pip list

RUN pip install -e /sweeper


WORKDIR /sweeper

ENTRYPOINT [ "/bin/bash" ]
