# pull official base image
FROM python:3.9.6-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# make directory
RUN mkdir /prop_swift
WORKDIR /prop_swift

RUN apt-get update
RUN apt-get install -y cron && touch /var/log/cron.log

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /prop_swift/
RUN pip install -r requirements.txt

# copy project
COPY . /prop_swift/

ENTRYPOINT ["./entrypoint.sh"]
CMD ["./manage.py", "runserver", "0.0.0.0:8000"]

