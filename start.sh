#!/usr/bin/env bash
echo "=== Running migrations ==="
python manage.py migrate --run-syncdb
echo "=== Adding news data ==="
python manage.py add_news
echo "=== Starting server ==="
gunicorn indianews.wsgi:application --log-level info --access-logfile - --error-logfile -
