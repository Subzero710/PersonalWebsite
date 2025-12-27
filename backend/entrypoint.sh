#!/bin/sh
set -e

mkdir -p /app/staticfiles /app/media
chown -R appuser:appuser /app/staticfiles /app/media

su -p -s /bin/sh appuser -c "python manage.py migrate --noinput"
su -p -s /bin/sh appuser -c "python manage.py collectstatic --noinput"

exec su -p -s /bin/sh appuser -c "gunicorn Portfolio.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60"