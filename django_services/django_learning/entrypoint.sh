#!/bin/bash

SERVICE_NAME="$1"
CONTAINER_PORT="$2"

echo "Running database migrations"
python manage.py migrate --noinput

echo "Starting Gunicorn server on port $CONTAINER_PORT"
exec gunicorn -w 3 -b :$CONTAINER_PORT $SERVICE_NAME.wsgi:application
