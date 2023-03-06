# pull official base image
FROM python:3.9.6-alpine

RUN apk add --no-cache bash

# install crond
RUN apk add --no-cache dcron

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# make directory
RUN mkdir /prop_swift
WORKDIR /prop_swift

# django-crontab logfile
RUN mkdir /cron
RUN touch /cron/django_cron.log

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /prop_swift/
RUN pip install -r requirements.txt

# cron
ADD crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab


# copy project
COPY . /prop_swift/
CMD ["sh", "-c", "crond && python manage.py runserver 0.0.0.0:8000"]


