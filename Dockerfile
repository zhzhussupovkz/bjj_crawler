FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev python3-setuptools make git git-core \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY *.py *.yml *.json *.conf ./
COPY ./static ./static
COPY ./views ./views

ENV LC_ALL=C.UTF-8
