#!/bin/bash

SERVICE_NAME="$1"
CONTAINER_PORT="$2"
SUPERUSER_USERNAME="$3"
SUPERUSER_EMAIL="$4"
SUPERUSER_PASSWORD="$5"

echo "Running database migrations"
python manage.py migrate --noinput

echo "Creating superuser if it doesn't exist"
python manage.py create_superuser_if_not_exists \
    --username $SUPERUSER_USERNAME \
    --email $SUPERUSER_EMAIL \
    --password $SUPERUSER_PASSWORD

echo "Starting Gunicorn server on port $CONTAINER_PORT"
exec gunicorn -w 3 -b :$CONTAINER_PORT $SERVICE_NAME.wsgi:application
