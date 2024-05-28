#!/bin/bash

set -e

SERVICE_NAME="$1"
CONTAINER_PORT="$2"
SUPERUSER_USERNAME="$3"
SUPERUSER_EMAIL="$4"
SUPERUSER_PASSWORD="$5"
WORKERS_PER_INSTANCE="$6"

echo "Running database migrations"
python manage.py migrate --noinput

echo "Creating superuser if it doesn't exist"
python manage.py create_superuser_if_not_exists \
    --username $SUPERUSER_USERNAME \
    --email $SUPERUSER_EMAIL \
    --password $SUPERUSER_PASSWORD

echo "Collect static files, mainly for styling"
python manage.py collectstatic --noinput

echo "Initializing data in DB"
python manage.py init_db

echo "Starting Gunicorn server on port $CONTAINER_PORT"
exec gunicorn -w $WORKERS_PER_INSTANCE -b :$CONTAINER_PORT $SERVICE_NAME.wsgi:application
