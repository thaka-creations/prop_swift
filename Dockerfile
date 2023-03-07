# pull official base image
FROM python:3.9.6-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# make directory
RUN mkdir /prop_swift
WORKDIR /prop_swift

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /prop_swift/
RUN pip install -r requirements.txt

# django-crontab logfine
RUN mkdir /cron
RUN touch /cron/cronjob.log

# copy project
COPY . /prop_swift/

CMD service cron start && python3 manage.py crontab add && python3 manage.py runserver 0.0.0.0:8000


