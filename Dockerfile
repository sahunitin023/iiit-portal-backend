FROM python:3.12-slim

ENV PYTHONBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /iiit-portal

COPY . .

RUN apt-get update

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD gunicorn backend.wsgi:application --bind 0.0.0.0:8000

EXPOSE 8000
