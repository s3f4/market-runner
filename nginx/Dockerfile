FROM nginx:latest

MAINTAINER Sefa ŞAHİN <sefa@dehaa.com>


RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf

COPY market-runner.conf /etc/nginx/conf.d/