FROM python:3.12-alpine3.21
LABEL maintainer="nikolajtarasenko71@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


RUN adduser \
        --disabled-password \
        --no-create-home \
        my_user

RUN mkdir -p /files/media
RUN chown -R my_user /files/media
RUN chmod -R 755 /files/media

RUN python manage.py collectstatic --noinput


USER my_user
