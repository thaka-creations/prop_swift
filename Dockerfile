# pull official base image
FROM python:3.9.6-alpine

RUN apk add --no-cache bash

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

# copy project
COPY . /prop_swift/


