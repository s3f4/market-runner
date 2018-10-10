FROM python:3.6

MAINTAINER Sefa ŞAHİN <sefa@dehaa.com>

RUN mkdir -p /usr/src/app
RUN apt-get update
RUN apt-get install  -y python3-pip

WORKDIR /usr/src/app
COPY ./requirements.txt /usr/src/app/
RUN pwd
RUN ls -la
RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt

COPY . /usr/src/app
RUN ls  -la