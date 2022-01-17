# syntax=docker/dockerfile:1

FROM python:3.11.0a3-bullseye
WORKDIR /app

RUN pip3 install --upgrade pip
COPY . /app/
RUN pip3 install /app
