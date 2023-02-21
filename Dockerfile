# pull official base image
FROM python:3.9.6-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# make directory
RUN mkdir /analytics
WORKDIR /analytics

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /analytics/
RUN pip install -r requirements.txt

# copy project
COPY . /analytics/

